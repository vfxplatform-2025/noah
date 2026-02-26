class NoahData():
    def __init__(self):

        self.fileType = [
            'alembic', 'alembicCurve', 'ass', 'atom', 'camera', 'dummy',
            'maya', 'frameRange', 'geoCache', 'lookdev', 'modelEnv',
            'resolutionSet', 'rig', 'rigEnv', 'yetiCache', 'vdbFx',
            'vrayProxyFx', "lightRig", 'clarisse', 'digienv', 'instance'
        ]

        self.partType = [
            'ani', 'crowdSim', 'crowdAni', 'cloth', 'clothSim', "comp",
            'dyn', 'fur', 'furSim', 'fx', 'hair', 'hairSim',
            'lit', 'lookdev', 'layout', 'model', 'musle', "finalize",
            'matchmove', 'postviz', 'rig', 'render', 'simul',
            'litRig', 'mm', 'crowdPostviz', 'digienv', 'cfxCrowd'
        ]

        self.useType = [
            '', 'dummy'
        ]

        self.dataType = []

    def rootItem(self):
        self.dataType.extend(self.fileType)
        self.dataType.extend(self.partType)

        for fileName in self.fileType:
            for partName in self.partType:
                for useName in self.useType:
                    dataName = '{}{}{}'.format(fileName, partName[0].capitalize()+partName[1:], useName.capitalize())
                    self.dataType.append(dataName)

        for partName in self.partType:
            for fileName in self.fileType:
                for useName in self.useType:
                    dataName = '{}{}{}'.format(partName, fileName[0].capitalize()+fileName[1:], useName.capitalize())
                    self.dataType.append(dataName)

        dataType = list(set(self.dataType))
        return dataType
