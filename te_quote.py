import glob
import json
import os
import sys

from ai_automate_quote.auth.auth_manager import PinterestAuthenticator
from ai_automate_quote.upload.pinterest import PinterestUploader
from ai_automate_quote.utils.quote_text_to_auido_mix_video import TextToAudioMixVideo
from dotenv import load_dotenv
from ai_automate_quote.quotes.generator import QuoteGenerator
from ai_automate_quote.images.creator import TextImageGenerator
from ai_automate_quote.videos.creator import VideoCreator
from ai_automate_quote.download.drive import DriveManager
from ai_automate_quote.amazon.s3Manager import AmazonS3Manager
from ai_automate_quote.upload.youtube import YouTubeUploader
from ai_automate_quote.upload.facebook import FacebookUploader
from ai_automate_quote.upload.instagram import InstagramUploader
from ai_automate_quote.upload.pinterest import PinterestBoardManager

random_number = int(sys.argv[1])



def load_environment_variables():
    """Load and return environment variables."""
    load_dotenv()  # Ensure environment variables are loaded from the .env file.
    print(os.getenv('GEMENI_KEY'))
    env_vars = {
        "GEMENI_KEY": os.getenv('GEMENI_KEY'),
        "GEMENI_MODEL": os.getenv('GEMENI_MODEL'),
        "ADJECTIVES": os.getenv('ADJECTIVES').split(','),
        "THEMES": os.getenv('THEMES').split(','),
        "LANGUAGE": os.getenv('LANGUAGE'),
        "S3_ACCESS_KEY": os.getenv('S3_ACCESS_KEY'),
        "S3_SECRETE_KEY": os.getenv('S3_SECRETE_KEY'),
        "S3_ZONE": os.getenv('S3_ZONE'),
        "S3_BUCKET": os.getenv('S3_BUCKET'),
        "FB_VERSION": os.getenv('FB_VERSION'),
        "FB_PAGE_ID": os.getenv('FB_PAGE_ID'),
        "FB_PAGE_TOKEN": os.getenv('FB_PAGE_TOKEN'),
        "INSTA_PAGE_TOKEN":os.getenv('INSTA_PAGE_TOKEN'),
        "INSTA_PAGE_ID": os.getenv('INSTA_PAGE_ID'),
        "THREADS_VERSION": os.getenv('THREADS_VERSION'),
        "S3_URL": os.getenv('S3_URL'),
        "THREADS_PAGE_ID": os.getenv('THREADS_PAGE_ID'),
        "THREADS_PAGE_TOKEN": os.getenv('THREADS_PAGE_TOKEN'),
        "YT_JSON": os.getenv('YT_JSON'),
        "DRIVE_LINK": os.getenv('DRIVE_LINK'),
        "HF_TOKEN": os.getenv('HF_TOKEN'),
        "PINTEREST_CLIENT_ID": os.getenv('PINTEREST_CLIENT_ID'),
        "PINTEREST_CLIENT_SECRET": os.getenv('PINTEREST_CLIENT_SECRET'),
        "PINTEREST_ACCESS_TOKEN": os.getenv('PINTEREST_ACCESS_TOKEN'),
        "PINTEREST_REFRESH_TOKEN": os.getenv('PINTEREST_REFRESH_TOKEN'),
        "PINTEREST_API_URL": os.getenv('PINTEREST_API_URL'),
        "PINTEREST_BOARD_ID": os.getenv('PINTEREST_BOARD_ID'),
        "PINTEREST_STATIC_DOMINANT_COLOR": os.getenv('PINTEREST_STATIC_DOMINANT_COLOR'),
    }

    return env_vars


def download_files(music):
    """Download necessary files from Google Drive."""
    download = DriveManager(json.loads(os.getenv('YT_JSON')), [os.getenv('DRIVE_LINK')])
    download.build_drive_service()
    download.download_files([f"{music}.mp3", 'bg.png', 'font_te.ttf', 'output_image.png'])


def generate_quote(env_vars):
    """Generate a quote using the Quote Generator."""
    quote = QuoteGenerator(env_vars["GEMENI_KEY"], env_vars["GEMENI_MODEL"])
    quote.generateQuote(env_vars["ADJECTIVES"], env_vars["THEMES"], env_vars["LANGUAGE"])
    return quote


def create_image_and_video(music):
    """Create image and video based on the generated quote."""
    with open("quote_data.json", "r", encoding="utf-8") as quote_data:
        data = json.load(quote_data)  # ✅ load once
        quote_text = data['quote']
        image = TextImageGenerator('bg.png', 'font_te.ttf', 'output_image.png')
        image.text_on_background(quote_text)
        video = VideoCreator('output_image.png', f'{music}.mp3', output_video_path='temp_output_video.mp4', duration=55)
        print((quote_data))
        video.create_video_with_music()
        tts_mixer = TextToAudioMixVideo(text=quote_text, music_path=f'{music}.mp3')
        tts_mixer.process()



def upload_to_s3():
    """Upload the video to Amazon S3."""
    s3 = AmazonS3Manager(
        os.getenv('S3_ACCESS_KEY'),
        os.getenv('S3_SECRETE_KEY'),
        os.getenv('S3_ZONE'),
        os.getenv('S3_BUCKET')
    )
    url = s3.upload_file_to_s3('output_video.mp4', 'output_video_te.mp4')
    return url


def upload_to_platforms(quote_data):
    """Upload video to YouTube, Facebook, Instagram, and Threads."""
    yt = YouTubeUploader().initialize_upload(
        'output_video.mp4',
        quote_data['title'],
        quote_data['description'],
        quote_data['tags'],
        22, False
    )

    fb = FacebookUploader(quote_data, os.getenv('FB_VERSION'), os.getenv('FB_PAGE_ID'), os.getenv('FB_PAGE_TOKEN'))
    fb.initialize_upload_session('output_video.mp4')

    inst = InstagramUploader(quote_data, os.getenv('FB_VERSION'), os.getenv('INSTA_PAGE_ID'), os.getenv('INSTA_PAGE_TOKEN'))
    inst.post_reel(video_url='output_video.mp4')

    # th = ThreadsUploader(
    #     quote_data,
    #     os.getenv('THREADS_VERSION'),
    #     os.getenv('S3_URL'),
    #     os.getenv('THREADS_PAGE_ID'),
    #     os.getenv('THREADS_PAGE_TOKEN')
    # )
    # th.threads_post()
    pin_upload(quote_data,yt)
    
def pin_upload(quote_data,link):
    # Get access token
    print("🔐 Getting access token...")
    auth = PinterestAuthenticator()
    access_token = auth.get_access_token()
    board_id = os.getenv("PINTEREST_BOARD_ID")
    upload_url =  os.getenv("PINTEREST_API_URL") + 'pins'
    if not board_id:
        print("No Board ID provided in environment variable. Please select one Boards Id from below : ")
        pn = PinterestBoardManager(access_token)
        boards = pn.list_boards()
        print(boards)
        if not board_id:
            raise Exception("❌ No board selected. Aborting.")

    # Prepare uploader
    uploader = PinterestUploader(os.getenv("PINTEREST_ACCESS_TOKEN"), board_id,upload_url)

    # Find images
    image_paths = glob.glob("./output_image.png")
    if not image_paths:
        print("⚠️ No images found in ./assets/images/")
        return

    # Upload each image
    for img_path in image_paths:
        title = os.path.basename(img_path).split(".")[0].replace("_", " ").title()
        description = f"Auto-uploaded pin: {title}"
        video_url = f"https://www.youtube.com/watch?v={link}"
        try:
            res = uploader.create_pin_from_local(img_path,  quote_data['title'], quote_data['description'],os.getenv('PINTEREST_STATIC_DOMINANT_COLOR'),video_url)
            print(f"✅ Uploaded: {img_path} → Pin ID: {res.get('id', 'N/A')}")
        except Exception as e:
            print(f"❌ Error uploading {img_path}: {e}")

    print("🎉 All uploads completed!")


def main():
        music = random_number
        env_vars = load_environment_variables()
        download_files(music)
        generate_quote(env_vars)
        create_image_and_video(music)
        url = upload_to_s3()
        with open("quote_data.json", "r", encoding="utf-8") as quote_data_file:
            quote_data = json.load(quote_data_file)
            upload_to_platforms(quote_data)

if __name__ == "__main__":
    main()
    # YouTubeUploader().generate_auth_token()
