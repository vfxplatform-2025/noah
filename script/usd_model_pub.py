import os
from pathlib import Path

class UsdModelPub:
    def __init__(self, pubPath, fileName):
        self.pubPath = Path(pubPath)
        self.fileName = fileName
        # /show/ORV/assets/aircraft/test/model/pub/test_model_v01
        self.wipPath = self.pubPath.parents[1] / f'wip/data/usd/{self.fileName}'
        self.wipUsdPath = None
        self.renamedUsdPath = None
        if os.path.exists(str(self.wipPath)):
            usd_files = list(self.wipPath.glob('*.usd'))
            print(f'usd_files : {usd_files} <<<<<<<<<<<<<<<<<<<<')
            if usd_files:
                self.wipUsdPath = usd_files[0]

        if not self.wipUsdPath:
            print('============================================================')
            print(f'usd file not found. : {self.wipUsdPath}')
            print('============================================================')
            return
        # self.copyPupDir()
        # self.linkUsdFiles()
    def copyPupDir(self):
        target_file = self.pubPath / self.wipUsdPath.name
        if not target_file.exists():
            os.system(f"cp -rf {self.wipUsdPath} {self.pubPath}")
            mb_files = list(self.pubPath.glob('*.mb'))
            if mb_files:
                new_usd_name = mb_files[0].stem + '.usd'
                self.renamedUsdPath = self.pubPath / new_usd_name
                os.rename(target_file, self.renamedUsdPath)
                print(f"Renamed usd file to: {new_usd_name}")
            else:
                self.renamedUsdPath = target_file
            print(f"Copied {self.wipUsdPath} to {self.pubPath}")
        else:
            self.renamedUsdPath = target_file
            print(f"USD file already exists in {self.pubPath}: {target_file}")

    def linkUsdFiles(self):
        if self.renamedUsdPath and self.renamedUsdPath.exists():
            link_path = self.pubPath.parent / 'model.usd'
            if link_path.exists() or link_path.is_symlink():
                link_path.unlink()
            link_path.symlink_to(self.renamedUsdPath)
            print(f"Created symlink: {link_path} -> {self.renamedUsdPath}")
        else:
            print("No valid USD file to link.")

# if __name__ == '__main__':
#     UsdModelPub('/show/ORV/assets/aircraft/test/model/pub/test_model_v02', 'test_model_v02')

