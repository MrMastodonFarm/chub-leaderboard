#!/usr/bin/env python3
"""Submit text2img jobs to ComfyUI and download the results.

Usage: python3 comfy_gen.py <jobs.json>
jobs.json: {"checkpoint": "...", "width": 512, "height": 512,
            "steps": 28, "cfg": 6.5, "sampler": "euler", "scheduler": "normal",
            "negative": "...",
            "jobs": [{"name": "chris-farley", "prompt": "...", "seed": 11}, ...],
            "outdir": "/tmp/gen"}
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

BASE = "http://192.168.0.158:8188"


def api(path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def upload_image(path):
    """Upload a local image to ComfyUI's input dir; returns server filename."""
    name = os.path.basename(path)
    boundary = "----chubgen"
    with open(path, "rb") as fh:
        filedata = fh.read()
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="image"; filename="{name}"\r\n'
        "Content-Type: image/png\r\n\r\n"
    ).encode() + filedata + (
        f"\r\n--{boundary}\r\n"
        'Content-Disposition: form-data; name="overwrite"\r\n\r\ntrue\r\n'
        f"--{boundary}--\r\n"
    ).encode()
    req = urllib.request.Request(
        BASE + "/upload/image", data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())["name"]


def workflow(cfg, job):
    """Flux workflow: unet-only checkpoint + DualCLIPLoader + FluxGuidance."""
    return {
        "1": {"class_type": "CheckpointLoaderSimple",
              "inputs": {"ckpt_name": cfg["checkpoint"]}},
        "10": {"class_type": "DualCLIPLoader",
               "inputs": {"clip_name1": "clip_l.safetensors",
                          "clip_name2": "t5xxl_fp8_e4m3fn_scaled.safetensors",
                          "type": "flux"}},
        "11": {"class_type": "VAELoader",
               "inputs": {"vae_name": "ae.safetensors"}},
        "2": {"class_type": "CLIPTextEncode",
              "inputs": {"text": job["prompt"], "clip": ["10", 0]}},
        "12": {"class_type": "FluxGuidance",
               "inputs": {"conditioning": ["2", 0],
                          "guidance": cfg.get("guidance", 3.5)}},
        "3": {"class_type": "CLIPTextEncode",
              "inputs": {"text": cfg.get("negative", ""), "clip": ["10", 0]}},
        "4": {"class_type": "EmptyLatentImage",
              "inputs": {"width": cfg.get("width", 512),
                         "height": cfg.get("height", 512), "batch_size": 1}},
        "5": {"class_type": "KSampler",
              "inputs": {"model": ["1", 0], "positive": ["12", 0],
                         "negative": ["3", 0], "latent_image": ["4", 0],
                         "seed": job.get("seed", 0),
                         "steps": cfg.get("steps", 28),
                         "cfg": cfg.get("cfg", 1.0),
                         "sampler_name": cfg.get("sampler", "euler"),
                         "scheduler": cfg.get("scheduler", "simple"),
                         "denoise": job.get("denoise", 1.0)}},
        "6": {"class_type": "VAEDecode",
              "inputs": {"samples": ["5", 0], "vae": ["11", 0]}},
        "7": {"class_type": "SaveImage",
              "inputs": {"images": ["6", 0], "filename_prefix": job["name"]}},
    }


def img2img_nodes(wf, cfg, job):
    """Replace the empty latent with an encoded init image."""
    server_name = upload_image(job["image"])
    wf["20"] = {"class_type": "LoadImage", "inputs": {"image": server_name}}
    wf["21"] = {"class_type": "ImageScale",
                "inputs": {"image": ["20", 0], "upscale_method": "lanczos",
                           "width": cfg.get("width", 768),
                           "height": cfg.get("height", 768),
                           "crop": "center"}}
    wf["22"] = {"class_type": "VAEEncode",
                "inputs": {"pixels": ["21", 0], "vae": ["11", 0]}}
    wf["5"]["inputs"]["latent_image"] = ["22", 0]
    del wf["4"]
    return wf


def run_job(cfg, job, outdir):
    wf = workflow(cfg, job)
    if job.get("image"):
        wf = img2img_nodes(wf, cfg, job)
    pid = api("/prompt", {"prompt": wf})["prompt_id"]
    for _ in range(240):
        time.sleep(2)
        hist = api(f"/history/{pid}")
        if pid in hist:
            entry = hist[pid]
            status = entry.get("status", {})
            if status.get("status_str") == "error":
                msgs = [m for m in status.get("messages", [])
                        if m[0] == "execution_error"]
                raise RuntimeError(f"{job['name']}: {msgs}")
            for node in entry.get("outputs", {}).values():
                for img in node.get("images", []):
                    q = urllib.parse.urlencode(img)
                    dest = os.path.join(outdir, job["name"] + ".png")
                    with urllib.request.urlopen(f"{BASE}/view?{q}",
                                                timeout=60) as r:
                        with open(dest, "wb") as fh:
                            fh.write(r.read())
                    return dest
    raise RuntimeError(f"{job['name']}: timed out")


def main():
    with open(sys.argv[1]) as fh:
        cfg = json.load(fh)
    outdir = cfg.get("outdir", "/tmp/gen")
    os.makedirs(outdir, exist_ok=True)
    for job in cfg["jobs"]:
        t0 = time.time()
        dest = run_job(cfg, job, outdir)
        print(f"{job['name']}: {dest} ({time.time() - t0:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
