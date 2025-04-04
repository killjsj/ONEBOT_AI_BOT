function amdgpuinstall {
    pip install torch-directml
}
function cudainstall {
    echo '--- input your cuda version ---(run nvidia-smi.exe to check)'
    $name = Read-Host '11 or 12'
    if ($name -eq '11'){
        pip install torch<=2.2 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
        pip install nvidia-cudnn-cu11==8.9.7.29
        
    } elseif ($name -eq '12') {
        pip install torch<=2.2 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
        pip install nvidia-cudnn-cu12==8.9.7.29
    }
    echo "installing zlib"
    Invoke-WebRequest -Uri https://www.winimage.com/zLibDll/zlib123dllx64.zip -OutFile ./zlib123dllx64.zip
    $TempDir = [System.IO.Path]::GetTempPath()
    $systemdir = [System.Environment]::ExpandEnvironmentVariables("%SystemRoot%")
    Expand-Archive -Path ./zlib123dllx64.zip -DestinationPath $TempDir
    cd $TempDir/dll_x64
    cp *.* $systemdir
    echo 'zlib installed'
}
function cpuinstall {
    pip install torch<=2.2 torchvision torchaudio
}
$startat = ($pwd).Path
echo $startat
$name = Read-Host 'run ai on gpu/cpu?(n(no),amd(amd/intel gpu),cuda(nvidia gpu),cpu)'
if ($name -eq 'n'){
    $gpu = 0
}elseif ($name -eq 'amd') {
    $gpu = 1
}elseif ($name -eq 'cuda') {
    $gpu = 2
}elseif ($name -eq 'cpu') {
    $gpu = 3
}
echo 'discord pls check out https://github.com/ITCraftDevelopmentTeam/OneDisc/releases'
Write-Output "Installing...."
pip install -r req.txt
# git clone https://github.com/xinntao/Real-ESRGAN.git
cd Real-ESRGAN
python setup.py develop
switch ($gpu) {
    0 {}
    1 {amdgpuinstall}
    2 {cudainstall}
    3 {cpuinstall}
    Default {cpuinstall}
}
echo 'basicsr patching'
$sitePackagesPath = python -c "import site; print(site.getsitepackages()[0])"
$sitePackagesPath = Join-Path $sitePackagesPath "\Lib\site-packages"
Write-Output 'site-packages:' $sitePackagesPath
cd $startat
Copy-Item './basicsr' $sitePackagesPath -Recurse -Force
echo 'patched'
echo 'install end,pls restart pc'