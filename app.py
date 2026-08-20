from flask import Flask, render_template, request, send_file, abort, redirect
from yt_dlp import YoutubeDL
import os, uuid, glob, logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app=Flask(__name__)
os.makedirs("/tmp", exist_ok=True)

def get_opts():
    opts={"quiet":True, "no_warnings":True}
    if os.path.exists("cookies.txt"): 
        opts["cookiefile"]="cookies.txt"
    if os.path.exists("ffmpeg-8.0.1-essentials_build/bin/ffmpeg.exe"):
        opts["ffmpeg_location"]="ffmpeg-8.0.1-essentials_build/bin/ffmpeg.exe"
    elif os.path.exists("bin/ffmpeg"):
        opts["ffmpeg_location"]="bin/ffmpeg"
    return opts

def get_info(link):
    opts = get_opts()
    # Skip unnecessary processing for faster info extraction
    opts["skip_download"] = True
    opts["no_check_certificates"] = True
    with YoutubeDL(opts) as ydl:
        return ydl.extract_info(link, download=False)

def get_direct_url(link, ftype):
    """Extract a direct CDN URL for MP4 (avoids proxying through our server)."""
    opts = get_opts()
    opts["skip_download"] = True
    opts["no_check_certificates"] = True
    if ftype == "mp4":
        opts["format"] = "best[ext=mp4]/best"
    else:
        opts["format"] = "bestaudio/best"
    with YoutubeDL(opts) as ydl:
        info = ydl.extract_info(link, download=False)
        return info.get("url")

def download_file(link, ftype):
    name=str(uuid.uuid4())
    opts=get_opts()
    opts["outtmpl"]=f"/tmp/{name}.%(ext)s"
    opts["no_check_certificates"] = True
    
    if ftype=="mp3":
        opts["format"]="bestaudio/best"
        opts["postprocessors"]=[{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192"
        }]
    else:
        opts["format"]="best[ext=mp4]/best"
    
    with YoutubeDL(opts) as ydl:
        ydl.extract_info(link, download=True)
        
    # Find and return the downloaded file
    return glob.glob(f"/tmp/{name}.*")[0]

def handle_error(e):
    msg=str(e)
    logger.error("Request error: %s", msg)
    if "cookies" in msg.lower(): msg="Please add a valid cookies.txt file."
    if "cannot parse data" in msg.lower(): msg="This link could not be processed. The platform may have changed its format. Please try a different link or try again later."
    return render_template("error.html", error_message=msg)

def safe_download_and_send(link, ftype):
    """Download, send, and clean up temp files."""
    # For MP4: redirect to CDN directly (much faster, no server download needed)
    if ftype == "mp4":
        try:
            direct_url = get_direct_url(link, ftype)
            if direct_url:
                return redirect(direct_url)
        except Exception:
            logger.warning("Direct URL failed, falling back to proxy download")
    
    # For MP3 or fallback: download on server then send
    filepath = download_file(link, ftype)
    try:
        response = send_file(filepath, as_attachment=True)
        @response.call_on_close
        def cleanup():
            try:
                os.remove(filepath)
            except OSError:
                pass
        return response
    except Exception:
        try:
            os.remove(filepath)
        except OSError:
            pass
        raise

@app.route("/favicon.ico")
def favicon():
    return abort(204)

# --- PAGES ---
@app.route("/")
def home(): 
    return render_template("main.html")

@app.route("/instagram")
def instagram_page(): 
    return render_template("index2.html")

@app.route("/facebook")
def facebook_page(): 
    return render_template("index3.html")

@app.route("/twitter")
def twitter_page(): 
    return render_template("index4.html")


# --- INSTAGRAM ---
@app.route("/instagram/api", methods=["POST"])
def instagram_preview():
    try:
        link = request.form.get("link_input")
        if "instagram" not in link.lower(): return render_template("error.html", error_message="Invalid link")
        info = get_info(link)
        return render_template("result2.html", title=info.get("title"), thumbnail_url=info.get("thumbnail"), link_input=link, ftype=request.form.get("file_type"))
    except Exception as e: return handle_error(e)

@app.route("/instagram/download")
def instagram_download():
    try: return safe_download_and_send(request.args.get("link"), request.args.get("type"))
    except Exception as e: return handle_error(e)


# --- FACEBOOK ---
@app.route("/facebook/api", methods=["POST"])
def facebook_preview():
    try:
        link = request.form.get("link_input")
        if "facebook" not in link.lower(): return render_template("error.html", error_message="Invalid link")
        info = get_info(link)
        return render_template("result3.html", title=info.get("title"), thumbnail_url=info.get("thumbnail"), link_input=link, ftype=request.form.get("file_type"))
    except Exception as e: return handle_error(e)


@app.route("/facebook/download")
def facebook_download():
    try: return safe_download_and_send(request.args.get("link"), request.args.get("type"))
    except Exception as e: return handle_error(e)


# --- TWITTER ---
@app.route("/twitter/api", methods=["POST"])
def twitter_preview():
    try:
        link = request.form.get("link_input")
        if "twitter" not in link.lower() and "x.com" not in link.lower(): return render_template("error.html", error_message="Invalid link")
        info = get_info(link)
        return render_template("result4.html", title=info.get("title"), thumbnail_url=info.get("thumbnail"), link_input=link, ftype=request.form.get("file_type"))
    except Exception as e: return handle_error(e)


@app.route("/twitter/download")
def twitter_download():
    try: 
        return safe_download_and_send(request.args.get("link"), request.args.get("type"))
    except Exception as e: 
        return handle_error(e)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

