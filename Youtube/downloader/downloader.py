from pytube import YouTube
import os


def download_video(video_url, resolution="1080p", output_folder="downloads"):
    try:
        # Créer le dossier de destination s'il n'existe pas
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        print(f"Fetching video details for: {video_url}")
        yt = YouTube(video_url)

        # Obtenir le flux correspondant à la résolution demandée
        video_stream = yt.streams.filter(res=resolution, progressive=True, file_extension='mp4').first()

        if not video_stream:
            print(f"Video with resolution {resolution} not available. Downloading best available quality.")
            video_stream = yt.streams.get_highest_resolution()

        print(f"Downloading: {yt.title} ({video_stream.resolution}) to {output_folder}")
        video_stream.download(output_path=output_folder)
        print("Download complete!")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    video_url = input("Enter the video URL: ")
    resolution = input("Enter the desired resolution (e.g., 720p, 1080p): ") or "1080p"
    output_folder = input("Enter the output folder (default: 'downloads'): ") or "downloads"
    download_video(video_url, resolution, output_folder)
