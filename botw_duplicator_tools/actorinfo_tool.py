import argparse
import pprint
import copy
import binascii
import io
from sys import argv

import wszst_yaz0
import byml
import pprint

def actorinfo_load(path):
    global is_yaz0
    with open(path, "rb") as file:
        actorinfo_rawdata = file.read()
    if actorinfo_rawdata[:4] == b"Yaz0":
        actorinfo_rawdata = wszst_yaz0.decompress(actorinfo_rawdata)
        is_yaz0 = True
    actorinfo_data = byml.Byml(actorinfo_rawdata).parse()
    return actorinfo_data

def actorinfo_save(data, path):
    
    if data:
        writer = byml.Writer(data, be=args.be, version=2)
        stream = io.BytesIO()
        writer.write(stream)
        stream.seek(0)
        actorinfo_rawdata = stream.read()
        
        if is_yaz0:
            actorinfo_rawdata = wszst_yaz0.compress(actorinfo_rawdata, level=10)
        with open(path, "wb") as file:
            file.write(actorinfo_rawdata)

def actorinfo_get(actorinfo_data, entry_name):
    try:
        entry_data = [entry for entry in actorinfo_data["Actors"] if entry["name"] == entry_name][0]
    except IndexError:
        print("'" + entry_name + "' is not in the ActorInfo file.")
        return
    pprint.pprint(entry_data)

def actorinfo_delete(actorinfo_data, entry_name):
    try:
        (id, entry_data) = [(id, entry) for (id, entry) in enumerate(actorinfo_data["Actors"]) if entry["name"] == entry_name][0]
    except IndexError:
        print("'" + entry_name + "' is not in the ActorInfo file.")
        return
    del actorinfo_data["Actors"][id]
    del actorinfo_data["Hashes"][id]
    return actorinfo_data

def actorinfo_copy_instsize(actorinfo_data, from_entry_name, to_entry_name):
    try:
        from_entry_data = [entry for entry in actorinfo_data["Actors"] if entry["name"] == from_entry_name][0]
    except IndexError:
        print("'" + from_entry_name + "' is not in the ActorInfo file.")
        return False
    try:
        to_entry_data = [entry for entry in actorinfo_data["Actors"] if entry["name"] == to_entry_name][0]
    except IndexError:
        print("'" + to_entry_name + "' is not in the ActorInfo file.")
        return False
    
    if to_entry_data["instSize"] < from_entry_data["instSize"]:
        to_entry_data["instSize"] = from_entry_data["instSize"]
    else:
        print("The instSize of '" + to_entry_name + "' is already greater than the instSize of '" + from_entry_name + "', so copying is unneccesary. The instSize was not copied.")
        return False
    
    return actorinfo_data

def actorinfo_duplicate(actorinfo_data, from_entry_name, to_entry_name):
    try:
        from_entry_data = [entry for entry in actorinfo_data["Actors"] if entry["name"] == from_entry_name][0]
    except IndexError:
        print("'" + from_entry_name + "' is not in the ActorInfo file.")
        return False
    
    try:
        [entry for entry in actorinfo_data["Actors"] if entry["name"] == to_entry_name][0]
        print("'" + to_entry_name + "' already exists in the ActorInfo file.")
        return False
    except IndexError:
        pass
    
    to_entry_data = copy.deepcopy(from_entry_data)
    to_entry_data["name"] = to_entry_name
    actorinfo_data = actorinfo_add(actorinfo_data, to_entry_data)
    return actorinfo_data

def actorinfo_add(actorinfo_data, new_entry_data):
    actorlist = [actor for actor in actorinfo_data["Actors"]]
    actorlist.append(new_entry_data)
    hashlist = [int(hash) for hash in actorinfo_data["Hashes"]]
    hashlist.append(int(binascii.crc32(new_entry_data["name"].encode()) & 0xffffffff))
    
    temp_list = zip(hashlist, actorlist)
    temp_list_sorted = sorted(temp_list)
    (new_hashlist, new_actorlist) = list(zip(*temp_list_sorted))
    
    actorinfo_data["Actors"] = [actor for actor in new_actorlist]
    actorinfo_data["Hashes"] = [byml.UInt(hash) for hash in new_hashlist]
    
    return actorinfo_data

def main():
    global is_yaz0
    global args
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--be", help="Use big endian (for Wii U files)", action="store_true")
    parser.add_argument("actorinfo_file", help="The ActorInfo.product.sbyml file you want to edit")
    subparsers = parser.add_subparsers()

    subparser_get = subparsers.add_parser("get", help="Get the data of an ActorInfo entry")
    subparser_get.set_defaults(subparser="get")
    subparser_get.add_argument("entry_name", help="The name of the entry to get the data from")

    subparser_delete = subparsers.add_parser("del", help="Delete an ActorInfo entry")
    subparser_delete.set_defaults(subparser="del")
    subparser_delete.add_argument("entry_name", help="The name of the entry to delete")

    subparser_duplicate = subparsers.add_parser("duplicate", help="Create a new ActorInfo entry by dulicating an old one")
    subparser_duplicate.set_defaults(subparser="duplicate")
    subparser_duplicate.add_argument("entry_to_duplicate", help="The name of the entry you want to duplicate")
    subparser_duplicate.add_argument("new_entry_name", help="The name you want for the new entry")

    subparser_copy_instsize = subparsers.add_parser("copy_instsize", help="Copy the value of a variable from one ActorInfo entry to another")
    subparser_copy_instsize.set_defaults(subparser="copy_instsize")
    subparser_copy_instsize.add_argument("from_entry_name", help="The name of the entry you want to copy the value from")
    subparser_copy_instsize.add_argument("to_entry_name", help="The name of the entry you want to copy the value to")

    args = parser.parse_args()

    ###

    is_yaz0 = True
    actorinfo_data = actorinfo_load(args.actorinfo_file)

    if (args.subparser == "get"):
        actorinfo_get(actorinfo_data, args.entry_name)
    if (args.subparser == "del"):
        actorinfo_data = actorinfo_delete(actorinfo_data, args.entry_name)
        actorinfo_save(actorinfo_data, args.actorinfo_file)
    if (args.subparser == "copy_instsize"):
        actorinfo_data = actorinfo_copy_instsize(actorinfo_data, args.from_entry_name, args.to_entry_name)
        actorinfo_save(actorinfo_data, args.actorinfo_file)
    if (args.subparser == "duplicate"):
        actorinfo_data = actorinfo_duplicate(actorinfo_data, args.entry_to_duplicate, args.new_entry_name)
        actorinfo_save(actorinfo_data, args.actorinfo_file)

if __name__ == '__main__':
    main()