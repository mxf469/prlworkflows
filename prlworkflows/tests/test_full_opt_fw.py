from pymatgen import Structure
from fireworks import Firework
from pymatgen.io.vasp.sets import MPRelaxSet
from prlworkflows.prl_fireworks import FullOptFW
from prlworkflows.input_sets import PRLRelaxSet
import pytest
import shutil
import os

POSCAR_STR = """Si2
1.0
3.840198 0.000000 0.000000
1.920099 3.325710 0.000000
0.000000 -2.217138 3.135509
Si
2
direct
0.000000 0.000000 0.000000 Si
0.750000 0.500000 0.750000 Si"""

struct = Structure.from_str(POSCAR_STR, fmt='POSCAR')


TEST_DIR = 'tmp_fw_test_dir'

@pytest.fixture
def launch_dir():
    os.mkdir(TEST_DIR)
    os.chdir(TEST_DIR)
    yield
    os.chdir('..')
    shutil.rmtree(TEST_DIR)
    return

def test_full_opt_fw_writes_correct_fw_for_UIS_in_set_constructor(launch_dir):
    s = PRLRelaxSet(struct, user_incar_settings={'ISIF': 4})
    fw = FullOptFW(struct, vasp_input_set=s, vasp_cmd=None)
    # reconstitute the FW
    fw_recon = Firework.from_dict(fw.as_dict())
    vis_recon = fw_recon.tasks[0].get('vasp_input_set')
    # check that UIS exists
    assert isinstance(vis_recon, PRLRelaxSet)
    assert vis_recon.user_incar_settings == {'ISIF': 4}
    assert vis_recon.incar.as_dict()['ISIF'] == 4


def test_full_opt_fw_writes_isif_setting_takes_effect(launch_dir):
    fw = FullOptFW(struct, isif=7, vasp_cmd=None)
    # reconstitute the FW
    fw_recon = Firework.from_dict(fw.as_dict())
    vis_recon = fw_recon.tasks[0].get('vasp_input_set')
    # check that UIS exists
    assert isinstance(vis_recon, PRLRelaxSet)
    assert vis_recon.user_incar_settings == {'ISIF': 7}
    assert vis_recon.incar.as_dict()['ISIF'] == 7



def test_full_opt_fw_writes_isif_setting_does_not_take_effect_with_VIS(launch_dir):
    s = PRLRelaxSet(struct)
    fw = FullOptFW(struct, vasp_input_set=s, isif=7, vasp_cmd=None)
    # reconstitute the FW
    fw_recon = Firework.from_dict(fw.as_dict())
    vis_recon = fw_recon.tasks[0].get('vasp_input_set')
    # check that UIS exists
    assert isinstance(vis_recon, PRLRelaxSet)
    assert vis_recon.user_incar_settings == {}
    assert vis_recon.incar.as_dict()['ISIF'] == 3
