#!/bin/bash
#SBATCH -J down_gee
#SBATCH --partition=priority
#SBATCH --account=zhz18039
#SBATCH --nodes 1
#SBATCH --ntasks 1
#SBATCH --array 1-20
#SBATCH --mem-per-cpu=10G
#SBATCH -o log/%x-out-%A_%4a.out
#SBATCH -e log/%x-err-%A_%4a.err


. "/home/shq19004/miniconda3/etc/profile.d/conda.sh"  # startup conda
conda activate nightlight  # activate the conda environment

echo $SLURMD_NODENAME # display the node name
cd ../

# jobs for downloading HLS data from GEE for mutiple locations
PRODUCT='HLS'
DATE='20130411-20241231'
EXTENT='[-76.6684662,38.82467197,-76.42889892,38.98579013]'
DES='/gpfs/sharedfs1/zhulab/Shi/ProjectSythetic/Test/SERC'

SENSOR='L30'
BANDS='B2,B3,B4,B5,B6,B7,Fmask'
python batch_download.py --ci=$SLURM_ARRAY_TASK_ID --cn=$SLURM_ARRAY_TASK_MAX --product=$PRODUCT --sensor=$SENSOR --date=$DATE --bands=$BANDS --extent=$EXTENT --destination=$DES 
SENSOR='S30'
BANDS='B2,B3,B4,B8A,B11,B12,Fmask'
python batch_download.py --ci=$SLURM_ARRAY_TASK_ID --cn=$SLURM_ARRAY_TASK_MAX --product=$PRODUCT --sensor=$SENSOR --date=$DATE --bands=$BANDS --extent=$EXTENT --destination=$DES 

EXTENT='[-68.82500705,45.11237216,-68.60006578,45.27336056]'
DES='/gpfs/sharedfs1/zhulab/Shi/ProjectSythetic/Test/HowlandForest'
SENSOR='L30'
BANDS='B2,B3,B4,B5,B6,B7,Fmask'
python batch_download.py --ci=$SLURM_ARRAY_TASK_ID --cn=$SLURM_ARRAY_TASK_MAX --product=$PRODUCT --sensor=$SENSOR --date=$DATE --bands=$BANDS --extent=$EXTENT --destination=$DES 
SENSOR='S30'
BANDS='B2,B3,B4,B8A,B11,B12,Fmask'
python batch_download.py --ci=$SLURM_ARRAY_TASK_ID --cn=$SLURM_ARRAY_TASK_MAX --product=$PRODUCT --sensor=$SENSOR --date=$DATE --bands=$BANDS --extent=$EXTENT --destination=$DES 

EXTENT='[-115.79578886,38.400624,-115.57312436,38.6060549]'
DES='/gpfs/sharedfs1/zhulab/Shi/ProjectSythetic/Test/RailroadValley'
SENSOR='L30'
BANDS='B2,B3,B4,B5,B6,B7,Fmask'
python batch_download.py --ci=$SLURM_ARRAY_TASK_ID --cn=$SLURM_ARRAY_TASK_MAX --product=$PRODUCT --sensor=$SENSOR --date=$DATE --bands=$BANDS --extent=$EXTENT --destination=$DES 
SENSOR='S30'
BANDS='B2,B3,B4,B8A,B11,B12,Fmask'
python batch_download.py --ci=$SLURM_ARRAY_TASK_ID --cn=$SLURM_ARRAY_TASK_MAX --product=$PRODUCT --sensor=$SENSOR --date=$DATE --bands=$BANDS --extent=$EXTENT --destination=$DES 

EXTENT='[-106.50812095,32.75797882,-106.14617191,33.08320348]'
DES='/gpfs/sharedfs1/zhulab/Shi/ProjectSythetic/Test/WhiteSands'
SENSOR='L30'
BANDS='B2,B3,B4,B5,B6,B7,Fmask'
python batch_download.py --ci=$SLURM_ARRAY_TASK_ID --cn=$SLURM_ARRAY_TASK_MAX --product=$PRODUCT --sensor=$SENSOR --date=$DATE --bands=$BANDS --extent=$EXTENT --destination=$DES 
SENSOR='S30'
BANDS='B2,B3,B4,B8A,B11,B12,Fmask'
python batch_download.py --ci=$SLURM_ARRAY_TASK_ID --cn=$SLURM_ARRAY_TASK_MAX --product=$PRODUCT --sensor=$SENSOR --date=$DATE --bands=$BANDS --extent=$EXTENT --destination=$DES 

echo 'Finished!'
exit

#SBATCH --partition=general

#SBATCH --partition=priority
#SBATCH --account=zhz18039


#SBATCH --partition=priority
#SBATCH --account=zhz18039
#SBATCH --nodes 1
#SBATCH --ntasks 1
#SBATCH --array 1-170
#SBATCH --exclude=cn[244,245,246,252,254,255,268,269,270,271,285,289,290,291,293]