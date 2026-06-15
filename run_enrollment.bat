@echo off
call conda activate learning
python d:\cnn_sys\camera_system\enroll.py enroll --matricule UCC2026001 --nom Mvemba --prenom DieuMerci --photos d:\cnn_sys\Dataset\dieumerci_20260612_075801.jpg d:\cnn_sys\Dataset\dm_20260612_075844.jpg d:\cnn_sys\Dataset\dm_20260612_080001.jpg d:\cnn_sys\Dataset\dm_20260612_080024.jpg
pause
