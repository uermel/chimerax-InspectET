import os
import s3fs
from cryoet_alignment.io.imod import ImodAlignment, ImodXF, ImodTLT, ImodXTILT, ImodTILTCOM, ImodNEWSTCOM
from cryoet_alignment.io.aretomo3 import AreTomo3ALN
from cryoet_alignment.io.cryoet_data_portal import Alignment


def imod_from_s3(s3_basename: str):
    fs = s3fs.S3FileSystem()

    with fs.open(f"{s3_basename}.xf", "r") as file:
        xf = ImodXF.from_stream(file)

    with fs.open(f"{s3_basename}.tlt", "r") as file:
        tlt = ImodTLT.from_stream(file)

    if fs.exists(f"{s3_basename}.xtilt"):
        with fs.open(f"{s3_basename}.xtilt", "r") as file:
            xtilt = ImodXTILT.from_stream(file)
    else:
        xtilt = None

    directory = os.path.dirname(s3_basename)
    if fs.exists(f"{directory}/tilt.com"):
        with fs.open(f"{directory}/tilt.com", "r") as file:
            tiltcom = ImodTILTCOM.from_stream(file)
    else:
        tiltcom = None

    if fs.exists(f"{directory}/newst.com"):
        with fs.open(f"{directory}/newst.com", "r") as file:
            newstcom = ImodNEWSTCOM.from_stream(file)
    else:
        newstcom = None

    return ImodAlignment(xf=xf, tlt=tlt, xtilt=xtilt, tiltcom=tiltcom, newstcom=newstcom)


def aretomo3_from_s3(path: str):
    fs = s3fs.S3FileSystem()
    with fs.open(path, "r") as f:
        aln = AreTomo3ALN.from_stream(f)

    return aln


def cdp_from_s3(path: str):
    fs = s3fs.S3FileSystem()
    with fs.open(path, "r") as f:
        ali = Alignment.from_stream(f)

    return ali
