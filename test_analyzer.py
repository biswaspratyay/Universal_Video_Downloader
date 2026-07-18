from backend.analyzer import VideoAnalyzer

url = input("Video URL: ")

analyzer = VideoAnalyzer()

info = analyzer.analyze(url)

print()
print("Title:", info.title)
print("Uploader:", info.uploader)
print("Duration:", info.duration)
print("Views:", info.view_count)
print("Formats:", len(info.formats))

print()

for fmt in info.formats:
    print(fmt.display_name)
