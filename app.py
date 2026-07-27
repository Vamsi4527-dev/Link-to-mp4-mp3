from flask import Flask, render_template, request, send_file
from yt_dlp import YoutubeDL
import os
import uuid
import re

ANSI_ESCAPE=re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

def clean_error(msg):
    """Strip ANSI escape codes and return a readable error string."""
    cleaned=ANSI_ESCAPE.sub('', str(msg))
    # Provide a friendlier message for Instagram auth errors
    if 'empty media response' in cleaned or 'cookies' in cleaned.lower() and 'instagram' in cleaned.lower():
        return ("Instagram requires authentication to access this post. "
                "Please make sure your cookies.txt file contains valid Instagram session cookies. "
                "Export them from your browser using a cookies.txt extension while logged into Instagram.")
    return cleaned

app=Flask(__name__)

DOWNLOAD_FOLDER="/tmp"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

INSTAGRAM_PATTERN=re.compile(
    r"^https?://(www\.)?instagram\.com/(reel|p|tv)/",
    re.IGNORECASE
)

FACEBOOK_PATTERN=re.compile(
    r"^https?://(www\.|m\.|web\.)?facebook\.com/",
    re.IGNORECASE
)

TWITTER_PATTERN=re.compile(
    r"^https?://(www\.)?(twitter\.com|x\.com)/",
    re.IGNORECASE
)


def preview_video(link):
    ydl_opts={
        "quiet":True
    }
    
    cookie_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookies.txt")
    if os.path.exists(cookie_path):
        ydl_opts["cookiefile"]=cookie_path
        
    with YoutubeDL(ydl_opts) as ydl:
        info=ydl.extract_info(link,download=False)

    return {
        "title":info.get("title","Video"),
        "thumbnail":info.get("thumbnail"),
        "author":info.get("uploader","Unknown"),
        "length":info.get("duration",0)
    }


def download_video(link,file_type):
    unique_id=str(uuid.uuid4())
    output_template=os.path.join(DOWNLOAD_FOLDER,f"{unique_id}.%(ext)s")

    if file_type=="mp3":
        ydl_opts={
            "outtmpl":output_template,
            "format":"bestaudio/best",
            "quiet":True
        }
    else:
        ydl_opts={
            "outtmpl":output_template,
            "format":"bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
            "merge_output_format":"mp4",
            "quiet":True
        }
    
    cookie_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),"cookies.txt")
    if os.path.exists(cookie_path):
        ydl_opts["cookiefile"]=cookie_path

    with YoutubeDL(ydl_opts) as ydl:
        info=ydl.extract_info(link,download=True)
        file_path=ydl.prepare_filename(info)

    if file_type=="mp4":
        return file_path

    mp3_path=os.path.join(DOWNLOAD_FOLDER,f"{unique_id}.mp3")
    project_dir=os.path.dirname(os.path.abspath(__file__))
    local_ffmpeg_bin=os.path.join(project_dir,"ffmpeg-8.0.1-essentials_build","bin","ffmpeg.exe")
    ffmpeg_cmd=f'"{local_ffmpeg_bin}"' if os.path.exists(local_ffmpeg_bin) else "ffmpeg"
    
    os.system(f'{ffmpeg_cmd}-i"{file_path}"-vn-acodec libmp3lame"{mp3_path}"-y')
    if os.path.exists(file_path) and file_path!=mp3_path:
        try:
            os.remove(file_path)
        except Exception:
            pass

    return mp3_path


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


@app.route("/instagram/api",methods=["POST"])
def instagram_preview():
    try:
        link=request.form.get("link_input")
        file_type=request.form.get("file_type")

        if not INSTAGRAM_PATTERN.match(link):
            return render_template("error.html",error_message="Invalid Instagram link")

        info=preview_video(link)

        return render_template(
            "result2.html",
            title=info["title"],
            thumbnail_url=info["thumbnail"],
            link_input=link,
            ftype=file_type
        )

    except Exception as e:
        return render_template("error.html",error_message=clean_error(e))


@app.route("/instagram/download")
def instagram_download():
    try:
        link=request.args.get("link")
        file_type=request.args.get("type","mp4")

        file_path=download_video(link,file_type)

        return send_file(file_path,as_attachment=True)

    except Exception as e:
        return render_template("error.html",error_message=clean_error(e))


@app.route("/facebook/api",methods=["POST"])
def facebook_preview():
    try:
        link=request.form.get("link_input")
        file_type=request.form.get("file_type")

        if not FACEBOOK_PATTERN.match(link):
            return render_template("error.html",error_message="Invalid Facebook link")

        info=preview_video(link)

        return render_template(
            "result3.html",
            title=info["title"],
            thumbnail_url=info["thumbnail"],
            link_input=link,
            ftype=file_type
        )

    except Exception as e:
        return render_template("error.html",error_message=clean_error(e))


@app.route("/facebook/download")
def facebook_download():
    try:
        link=request.args.get("link")
        file_type=request.args.get("type","mp4")

        file_path=download_video(link,file_type)

        return send_file(file_path,as_attachment=True)

    except Exception as e:
        return render_template("error.html",error_message=clean_error(e))


@app.route("/twitter/api",methods=["POST"])
def twitter_preview():
    try:
        link=request.form.get("link_input")
        file_type=request.form.get("file_type")

        if not TWITTER_PATTERN.match(link):
            return render_template("error.html",error_message="Invalid Twitter / X link")

        info=preview_video(link)

        return render_template(
            "result4.html",
            title=info["title"],
            thumbnail_url=info["thumbnail"],
            link_input=link,
            ftype=file_type
        )

    except Exception as e:
        return render_template("error.html",error_message=clean_error(e))


@app.route("/twitter/download")
def twitter_download():
    try:
        link=request.args.get("link")
        file_type=request.args.get("type","mp4")

        file_path=download_video(link,file_type)

        return send_file(file_path,as_attachment=True)

    except Exception as e:
        return render_template("error.html",error_message=clean_error(e))


if __name__=="__main__":
    app.run(debug=True)