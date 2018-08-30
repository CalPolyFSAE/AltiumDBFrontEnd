class Part:
    def __init__(self, manuID, drawer, name, value, package, mfrPartNo,
                 purchaseLink, description, comment, datasheetLink, supplier, supplierPN,
                 creator, libraryRef, libraryPath, footprintRef, footprintPath):

        self.name = None
        self.manID = None
        self.drawerID = None
        self.value = None
        self.package = None
        self.manPN = None
        self.PNLink = None
        self.desc = None
        self.comment = None
        self.datasheet = None
        self.supplier = 'Digi-Key'
        self.suppPN = None
        self.creator = None
        self.libRef = None
        self.libPath = None
        self.footRef = None
        self.footPath = None
        self.genName()

    def genName(self):
        pass
