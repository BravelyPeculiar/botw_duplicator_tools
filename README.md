

## Installation
Install Python 3.6+, then run `pip install botw-duplicator-tools`.

## Documentation
### actorinfo_tool
Use `-b` for big-endian (Wii U) files.

##### Get entry data
`actorinfo_tool [-b] ACTORINFO_FILE get ENTRY_NAME`

(e.g. `actorinfo_tool -b ActorInfo.product.sbyml get Armor_001_Head`)

##### Delete entry
`actorinfo_tool [-b] ACTORINFO_FILE del ENTRY_NAME`

##### Duplicate entry
For making new actors.

`actorinfo_tool [-b] ACTORINFO_FILE duplicate ENTRY_TO_DUPLICATE NEW_ENTRY_NAME`

##### Copy `instSize`
For putting armor models over other armors

`actorinfo_tool [-b] ACTORINFO_FILE copy_instsize FROM_ENTRY_NAME TO_ENTRY_NAME`

### actorpack\_tool
Use `-b` for big-endian (Wii U) files.

##### Rename file inside pack                             
`actorpack_tool [-b] ACTORPACK rename_file FILE_EXTENSION NEW_NAME` 

(e.g. `actorpack_tool -b Enemy_Bokoblin_Junior.sbactorpack rename_file baiprog Enemy_Haha_Lol.baiprog` )

##### Copy model and physics from one actor to another
For putting an armor over a different existing armor. Use `-b` for big-endian (Wii U) files.

`actorpack_tool [-b] ACTORPACK copy_model FROM_ACTORPACK`

### bfres\_duplicator
For correctly duplicating bfres files (also works on bitemico files). The name of the new bfres must be same length as the name of the original bfres.

(Simply copy-pasting the bfres/bitemico file won't make the required internal changes to the file).

`bfres_duplicator.py OLD_FILE_PATH NEW_FILE_PATH`

## Guides
#### To put a duplicate of an armor's model (and physics) over a different one:
This example will put `Armor_001_Head` over `Armor_050_Head`, and `Armor_002_Lower` over `Armor_050_Lower`.

1.
    * `bfres_duplicator [-b] path/to/Armor_001.sbfres path/to/Arm050Hed.sbfres` 
    * `bfres_duplicator [-b] path/to/Armor_002.sbfres path/to/Arm050Lwr.sbfres` 
Do this for their Tex1 and Tex2 as well. This will make new files for you to put your new models and icons into. Only the head part of Arm050Hed will be loaded, and the same for the lower part of Arm050Lwr.

2.
    * `actorpack_tool [-b] path/to/Armor_050_Head.sbactorpack copy_model path/to/Armor_001_Head.sbactorpack` 
    * `actorpack_tool [-b] path/to/Armor_050_Lower.sbactorpack copy_model path/to/Armor_002_Lower.sbactorpack` 
This will move the armors' paramater files for their models and physics over to a different actorpack. **Don't** follow the instructions about rstbtool.

3.
    * `actorpack_tool [-b] path/to/Armor_050_Head.sbactorpack rename_file bmodellist Arm050Hed` 
    * `actorpack_tool [-b] path/to/Armor_050_Lower.sbactorpack rename_file bmodellist Arm050Lwr` 
This will rename the .bmodellist files in the actorpacks so that you can safely edit them. Again, **don't** follow the instructions about rstbtool.

4. Inside `Armor_050_Head.sbactorpack`, open the `ModelUser/Arm050Hed.bmodellist`, and change all occurrences of `Armor_001` to `Arm050Hed`. This changes the bfres file that the actor will load.

5. Inside `Armor_050_Lower.sbactorpack`, open the `ModelUser/Arm050Lwr.bmodellist`, and change all occurrences of `Armor_002` to `Arm050Lwr`.

6. Use leoetlino's `rstbtool` on these files:
    * `Actor/Pack/Armor_050_Head.bactorpack`
    * `Actor/Pack/Armor_050_Lower.bactorpack`
    * `Actor/ActorLink/Armor_050_Head.bxml`
    * `Actor/ActorLink/Armor_050_Lower.bxml`

#### To make a whole new armor by duplicating an existing one:
This example will make a new Armor_999_Head out of Armor_001_Head.

1. `actorinfo_tool [-b] path/to/ActorInfo.product.sbyml duplicate Armor_001_Head Armor_999_Head` 
This creates an entry in ActorInfo.product.sbyml for your new actor, registering it with the game.

2. `bfres_duplicator [-b] path/to/Armor_001.sbfres path/to/Armor_999.sbfres` 
Do this for all 3 armor parts, including their Tex1 and Tex2, and also for all the associated .sbitemico files. This will make new files for you to put your new models and icons into.

3. Copy and paste `Armor_001_Head.sbactorpack` to make a new `Armor_999_Head.sbactorpack`.

4. `actorpack_tool [-b] path/to/Armor_001_Head.sbactorpack rename_file bmodellist Armor_999_Head` 
This will rename the .bmodellist file in the actorpack so that you can safely edit it. **Don't** follow the instructions about rstbtool.

5. Inside `Armor_999_Head.sbactorpack`, rename `ActorLink/Armor_001_Head.bxml` to `Armor_999_Head.bxml`.

6. Still inside `Armor_999_Head.sbactorpack`, open `ModelList/Armor_001_Head.bmodellist`, and change all occurrences of `Armor_001` to `Armor_999`. This changes the bfres file that the actor will load.

7. If you want to edit any other files in the actorpack, make sure to rename them to something new, and change the reference to the renamed file in the ActorLink .bxml to match the new name. This is because in BotW, files with the same name cannot have different content, even if they are in different .sbactorpacks. You can do this easily using the `rename_file` function of `actorpack_tool`.
