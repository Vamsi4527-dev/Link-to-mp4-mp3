# NexConvert 🚀

Hey! This is a simple web app I made that lets you download videos and audio from **YouTube, Instagram, Facebook, and Twitter/X**. Just paste a link, pick MP4 or MP3, and download it. That's it!

I built this using Python and Flask as a side project to learn web development.

---

## What can it do?

- Paste a YouTube, Instagram, Facebook, or Twitter/X link
- See a preview of the video (title + thumbnail)
- Download it as **MP4** (video) or **MP3** (audio)

It supports all 4 platforms from a single app!

---

## Tech I used

- **Python** - backend language
- **Flask** - web framework
- **pytubefix** - for downloading YouTube videos
- **yt-dlp** - for Instagram, Facebook, Twitter/X
- **FFmpeg** - for converting to MP3
- **HTML & CSS** - for the frontend pages

---

## Project Files

```
NEW_OWN_CONVERTER/
├── app.py               ← main backend code
├── requirements.txt     ← all required libraries
├── downloads/           ← downloaded files go here
├── static/
│   └── style.css        ← styling for the pages
└── templates/
    ├── main.html        ← home page (choose a platform)
    ├── index.html       ← YouTube page
    ├── index2.html      ← Instagram page
    ├── index3.html      ← Facebook page
    ├── index4.html      ← Twitter/X page
    ├── result.html      ← YouTube download page
    ├── result2.html     ← Instagram download page
    ├── result3.html     ← Facebook download page
    ├── result4.html     ← Twitter/X download page
    └── error.html       ← error page (if something goes wrong)
```

---

## How to run it

**Step 1 – Make sure you have Python and FFmpeg installed**

Check FFmpeg with:
```bash
ffmpeg -version
```

**Step 2 – Clone this repo**
```bash
git clone https://github.com/Vamsi4527-dev/Link-to-mp4-mp3.git
cd Link-to-mp4-mp3
```

**Step 3 – Install the required libraries**
```bash
pip install -r requirements.txt
```

**Step 4 – Run the app**
```bash
python app.py
```

**Step 5 – Open your browser and go to:**
```
http://127.0.0.1:5000/
```

That's it! The app should be running now.

---

## Routes / Pages

- `/` → Home page (pick YouTube, Instagram, Facebook, or Twitter)
- `/index` → YouTube downloader
- `/instagram` → Instagram downloader
- `/facebook` → Facebook downloader
- `/twitter` → Twitter/X downloader

---

## A few things to know

- Downloaded files are saved in the `downloads/` folder. You might want to clear it manually sometimes.
- YouTube uses `pytubefix`, everything else uses `yt-dlp` (they work differently under the hood).
- MP3 conversion is done using FFmpeg, so make sure it's installed.

---

## Disclaimer

Please use this responsibly. Downloading videos without permission might break the terms of service of these platforms. I'm not responsible for how you use this tool.
