import sys
import os
from src.database import Database

def main():

    assert len(sys.argv) >= 2, "Missing command"

    command = sys.argv[1]

    if command == "create":
        assert len(sys.argv) == 4, "Invalid number of arguments for calling create"
        assert os.path.isdir(sys.argv[2]), "Provided path is not a folder"

        db = Database(sys.argv[2])
        db.export(sys.argv[3])

"""
db = pickle.load(open("metallica.db", "rb"))

if isinstance(db, Database):
    marked_tracks = []
    needed_files = {}
    for track_head in db.track_db:
        # match track requirements
        if track_head.category == InstrumentCategory.GUITAR and track_head.is_drum == False:
            marked_tracks.append(track_head)
            needed_files[db.base_path + track_head.relative_file_path + track_head.file_name] = FilePath(track_head.relative_file_path,
                                                                                                         track_head.file_name,
                                                                                                         db.base_path)

    for fp in needed_files.values():
        container_list = get_container_list_from_file(fp, with_track=True)
        for track_container in container_list:
            if track_container.category == InstrumentCategory.GUITAR and track_container.is_drum == False:
                track_container.store_track_as_file("metallica_guitars/")
                """

if __name__ == '__main__':
    main()