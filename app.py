from flask import Flask, render_template, request, send_file
from yt_dlp import YoutubeDL
import os, uuid, glob

app=Flask(__name__)
os.makedirs("/tmp", exist_ok=True)

def get_opts():
    opts={"quiet":True}
    if os.path.exists("cookies.txt"): 
        opts["cookiefile"]="cookies.txt"
    if os.path.exists("ffmpeg-8.0.1-essentials_build/bin/ffmpeg.exe"):
        opts["ffmpeg_location"]="ffmpeg-8.0.1-essentials_build/bin/ffmpeg.exe"
    return opts

def get_info(link):
    with YoutubeDL(get_opts()) as ydl:
        return ydl.extract_info(link,download=False)

def download_file(link, ftype):
    name=str(uuid.uuid4())
    opts=get_opts()
    opts["outtmpl"]=f"/tmp/{name}.%(ext)s"
    
    if ftype=="mp3":
        opts["format"]="bestaudio/best"
        opts["postprocessors"]=[{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "0" # 0 means ffmpeg to use the highest possible VBR quality
        }]
    else:
        # download the best separate video and audio streams and merge them into an mp4
        opts["format"]="bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best"
        opts["merge_output_format"]="mp4"
    
    with YoutubeDL(opts) as ydl:
        ydl.extract_info(link, download=True)
        
    # Find and return the downloaded file
    return glob.glob(f"/tmp/{name}.*")[0]

def handle_error(e):
    msg=str(e)
    if "cookies" in msg.lower(): msg="Please add a valid cookies.txt file."
    return render_template("error.html", error_message=msg)

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
    try: return send_file(download_file(request.args.get("link"), request.args.get("type")), as_attachment=True)
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
    try: return send_file(download_file(request.args.get("link"), request.args.get("type")), as_attachment=True)
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
        return send_file(download_file(request.args.get("link"), request.args.get("type")), as_attachment=True)
    except Exception as e: 
        return handle_error(e)

if __name__ == "__main__":
    app.run(debug=True)
