import os
import google_auth_oauthlib
import googleapiclient.discovery
import googleapiclient.http
from dotenv import load_dotenv
from google import genai
import glob

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


# https://www.youtube.com/watch?v=sp3qM2URcig
def authenticate_youtube():
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    # Load client secrets file, put the path of your file
    client_secrets_file = os.getenv("CLIENT_SECRETS_FILE")

    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, SCOPES
    )
    credentials = flow.run_local_server()

    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

    return youtube


def describe_video(filename):
    extracted = filename[filename.index("_2026") + 1 :].replace(".mp4", "")
    with open(f"transcriptions/timestamp_{extracted}.txt", "r", encoding="utf-8") as f:
        video_content = f.read()
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    prompt = f""" Come up with a title (less than 70 characters), description, and 5 tags for a YouTube short with this transcript: {video_content}. Give it to me in the form title: <title>, etc. No text formatting. Give tags as tags: followed by a single line separated by commas. Do NOT add fluff."""
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    output_text = response.text
    print(f"Generated video description: {output_text}")
    return output_text


def upload_video(youtube, description, filename):
    lines = description.strip().split("\n")
    parsed = {}
    for line in lines:
        key, _, value = line.partition(": ")
        parsed[key.strip()] = value.strip()

    print(f"Parsed: {parsed}")  # DEBUG

    title = parsed.get("title", "")
    desc = parsed.get("description", "")
    tags = [tag.strip() for tag in parsed.get("tags", "").split(",")]

    # Build hashtags string from tags
    hashtags = " ".join(f"#{tag.replace(' ', '')}" for tag in tags)

    fixed = "#redditstories #viral"

    # Fixed in title, all hashtags in description
    title = f"{title} {fixed}"
    desc = f"{desc} {hashtags} {fixed}"

    request_body = {
        "snippet": {
            "categoryId": "24",
            "title": title,
            "description": desc,
            "tags": tags,
        },
        "status": {"privacyStatus": "public"},
    }

    media_file = filename

    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=googleapiclient.http.MediaFileUpload(
            media_file, chunksize=-1, resumable=True
        ),
    )

    response = None

    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload {int(status.progress()*100)}%")

        print(f"Video uploaded with ID: {response['id']}")


if __name__ == "__main__":
    youtube = authenticate_youtube()

    mp4_files = glob.glob("Upload/*.mp4")

    if not mp4_files:
        print("No MP4 files found in Upload folder.")
    else:
        while True:
            mp4_files = glob.glob("Upload/*.mp4")
            if not mp4_files:
                print("All videos uploaded, finishing...")
                break

            video_file = mp4_files[0]
            print(f"Uploading: {video_file}")
            description = describe_video(video_file)
            upload_video(youtube, description, video_file)
            print(f"Done: {video_file}")

            with open("uploaded_records.txt", "a", encoding="utf-8") as log:
                log.write(f"{os.path.basename(video_file)}\n")
            os.remove(video_file)
            print(f"Deleted {video_file} and logged to uploaded_records.txt")
