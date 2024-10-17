#!/bin/bash

amdgpuinstall() {
    pip install torch-directml
}

cudainstall() {
    echo '--- input your cuda version ---(run nvidia-smi to check)'
    read -p '11 or 12: ' name
    if [ "$name" = '11' ]; then
        pip install torch<=2.2 torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu118
        pip install nvidia-cudnn-cu11==8.9.7.29
    elif [ "$name" = '12' ]; then
        pip install torch<=2.2 torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu121
        pip install nvidia-cudnn-cu12==8.9.7.29
    fi
    echo "installing zlib"
    sudo apt-get install zlib1g-dev -y
    echo 'zlib installed'
}

cpuinstall() {
    pip install torch<=2.2 torchvision torchaudio
}

startat=$(pwd)
echo "Starting at $startat"
read -p 'run ai on gpu/cpu?(n(no),amd(amd/intel gpu),cuda(nvidia gpu),cpu): ' name
if [ "$name" = 'n' ]; then
    gpu=0
elif [ "$name" = 'amd' ]; then
    gpu=1
elif [ "$name" = 'cuda' ]; then
    gpu=2
elif [ "$name" = 'cpu' ]; then
    gpu=3
fi
echo 'discord pls check out https://github.com/ITCraftDevelopmentTeam/OneDisc/releases'
echo 'Installing...'
pip install -r req.txt
# git clone https://github.com/xinntao/Real-ESRGAN.git 
cd Real-ESRGAN
python setup.py develop
case $gpu in
    0)
        ;;
    1)
        amdgpuinstall
        ;;
    2)
        cudainstall
        ;;
    3)
        cpuinstall
        ;;
    *)
        cpuinstall
        ;;
esac
echo 'basicsr patching'
sitePackagesPath=$(python -c "import site; print(site.getsitepackages()[0])")
sitePackagesPath="$sitePackagesPath/Lib/site-packages"
echo 'site-packages:' $sitePackagesPath
cd "$startat"
cp -r ./basicsr "$sitePackagesPath"
echo 'patched'
echo 'install end, please restart your pc'