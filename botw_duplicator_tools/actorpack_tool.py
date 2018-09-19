import argparse
import os
import io

import sarc
import wszst_yaz0
import aamp

    
def load_actorpack(path, will_resave=True):
    global is_yaz0
    with open(path, "rb") as file:
        from_archive_rawdata = file.read()
    if from_archive_rawdata[:4] == b"Yaz0":
        from_archive_rawdata = wszst_yaz0.decompress(from_archive_rawdata)
        if will_resave:
            is_yaz0 = True
    archive = sarc.SARC(from_archive_rawdata)
    return archive
    
def save_actorpack(writer, path):
    stream = io.BytesIO()
    writer.write(stream)
    stream.seek(0)
    to_archive_rawdata = stream.read()
    if is_yaz0:
        to_archive_rawdata = wszst_yaz0.compress(to_archive_rawdata, level=10)
    with open(path, "wb") as file:
        file.write(to_archive_rawdata)

def rename_file(actorpack_path, ext, new_name):
    ext_dict = {
        "baiprog": "AIProgramUser",
        "baischedule": "AIScheduleUser",
        "baniminfo": "AnimationInfo",
        "baslist": "ASUser",
        "batcllist": "AttentionUser",
        "bawareness": "AwarenessUser",
        "bbonectrl": "BoneControlUser",
        "bchemical": "ChemicalUser",
        "bdmgparam": "DamageParamUser",
        "bdrop": "DropTableUser",
        "bgparamlist": "GParamUser",
        "blifecondition": "LifeConditionUser",
        "blod": "LODUser",
        "bmodellist": "ModelUser",
        "bphysics": "PhysicsUser",
        "brecipe": "RecipeUser",
        "brgbw": "RgBlendWeightUser",
        "brgconfiglist": "RgConfigListUser",
        "bshop": "ShopDataUser"
    }
    try:
        bxml_param_name = ext_dict[ext]
    except KeyError:
        print("'" + ext + "' is not a valid file extension to be renamed here.")
        exit()
    
    #Read
    archive = load_actorpack(actorpack_path)
    bxml_path = [filepath for filepath in archive.list_files() if filepath.endswith(".bxml")][0]
    bxml_rawdata = bytes(archive.get_file_data(bxml_path))
    bxml_data = aamp.Reader(bxml_rawdata).parse()
    bxml_data.list("param_root").object("LinkTarget").set_param(bxml_param_name, new_name)
    
    writer = aamp.Writer(bxml_data)
    stream = io.BytesIO()
    writer.write(stream)
    stream.seek(0)
    bxml_rawdata = stream.read()
    
    try:
        selected_file_path_old = [filepath for filepath in archive.list_files() if filepath.endswith("." + ext)][0]
    except IndexError:
        print("File with extension '." + ext + "' not fond in actorpack.")
        exit()
    selected_file_path_new = os.path.dirname(selected_file_path_old) + "/" + new_name + "." + ext
    selected_file_rawdata = bytes(archive.get_file_data(selected_file_path_old))
    print(selected_file_path_old)
    print(selected_file_path_new)
    
    #Write
    writer = sarc.make_writer_from_sarc(archive)
    writer.delete_file(selected_file_path_old)
    writer.add_file(selected_file_path_new, selected_file_rawdata)
    writer.add_file(bxml_path, bxml_rawdata)

    save_actorpack(writer, actorpack_path)
    
    actorpack_name = os.path.splitext(os.path.basename(actorpack_path))[0]
    print("You will need to use rstbtool on:")
    print("- 'Actor/Pack/" + actorpack_name + ".bactorpack'")
    print("- '" + bxml_path + "'")

def copy_model(from_actorpack_path, to_actorpack_path):
    files_to_add = []
    files_to_remove = []
    
    #from_actorpack
    from_archive = load_actorpack(from_actorpack_path, False)

    from_bphysics_path = [filepath for filepath in from_archive.list_files() if filepath.endswith(".bphysics")][0]
    from_bphysics_name = from_bphysics_path.split("/")[-1][:-9]
    from_bphysics_rawdata = bytes(from_archive.get_file_data(from_bphysics_path))
    files_to_add.append((from_bphysics_path, from_bphysics_rawdata))

    from_bmodellist_path = [filepath for filepath in from_archive.list_files() if filepath.endswith(".bmodellist")][0]
    from_bmodellist_name = from_bmodellist_path.split("/")[-1][:-11]
    from_bmodellist_rawdata = bytes(from_archive.get_file_data(from_bmodellist_path))
    files_to_add.append((from_bmodellist_path, from_bmodellist_rawdata))

    for file_path in from_archive.list_files():
        if file_path.startswith("Physics/"):
            file_rawdata = bytes(from_archive.get_file_data(file_path))
            files_to_add.append((file_path, file_rawdata))

    #to_actorpack read
    to_archive = load_actorpack(to_actorpack_path)

    to_bxml_path = [filepath for filepath in to_archive.list_files() if filepath.endswith(".bxml")][0]
    to_bxml_rawdata = bytes(to_archive.get_file_data(to_bxml_path))
    to_bxml_data = aamp.Reader(to_bxml_rawdata).parse()
    to_bxml_data.list("param_root").object("LinkTarget").set_param("ModelUser", from_bmodellist_name)
    to_bxml_data.list("param_root").object("LinkTarget").set_param("PhysicsUser", from_bphysics_name)

    writer = aamp.Writer(to_bxml_data)
    stream = io.BytesIO()
    writer.write(stream)
    stream.seek(0)
    to_bxml_rawdata = stream.read()
    files_to_add.append((to_bxml_path, to_bxml_rawdata))

    files_to_remove.append([filepath for filepath in to_archive.list_files() if filepath.endswith(".bphysics")][0])
    files_to_remove.append([filepath for filepath in to_archive.list_files() if filepath.endswith(".bmodellist")][0])
    files_to_remove.extend([filepath for filepath in to_archive.list_files() if filepath.startswith("Physics/")])

    #to_actorpack write
    writer = sarc.make_writer_from_sarc(to_archive)
    for file_path in files_to_remove:
        writer.delete_file(file_path)
    for file_path, file_rawdata in files_to_add:
        writer.add_file(file_path, file_rawdata)

    save_actorpack(writer, to_actorpack_path)
    
    to_actorpack_name = os.path.splitext(os.path.basename(to_actorpack_path))[0]
    print("You will need to use rstbtool on:")
    print("- 'Actor/Pack/" + to_actorpack_name + ".bactorpack'")
    print("- '" + to_bxml_path + "'")

def main():
    global is_yaz0
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--be", help="Use big endian (for Wii U files)", action="store_true")
    parser.add_argument("actorpack", help="The the actorpack you want to edit")
    subparsers = parser.add_subparsers()

    subparser_rename_file = subparsers.add_parser("rename_file", help="Rename a file inside the actorpack")
    subparser_rename_file.set_defaults(subparser="rename_file")
    subparser_rename_file.add_argument("file_extension", help="The extension of the file you want to rename (e.g. 'bmodellist')")
    subparser_rename_file.add_argument("new_name", help="The new name for the renamed file")

    subparser_copy_model = subparsers.add_parser("copy_model", help="Copy the model and physics from a different actorpack into this one")
    subparser_copy_model.set_defaults(subparser="copy_model")
    subparser_copy_model.add_argument("from_actorpack", help="The actorpack you want to take the model and physocs from")

    args = parser.parse_args()

    ###

    is_yaz0 = False
    if (args.subparser == "rename_file"):
        rename_file(args.actorpack, args.file_extension.lstrip("."), os.path.splitext(args.new_name)[0])
    if (args.subparser == "copy_model"):
        copy_model(args.from_actorpack, args.actorpack)

if __name__ == '__main__':
    main()