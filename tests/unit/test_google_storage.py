def test_download_file(google_storage):

    file = google_storage.download_file(filepath="perovskite/raw/idt1.txt")
    print(file)