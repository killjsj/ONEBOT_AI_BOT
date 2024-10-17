Write-Output "Installing...."
pip install opencv-python qrcode cnocr pydglab_ws pyautogui paddleocr paddlepaddle-gpu keras_ocr tensorflow==2.15.1 protobuf==3.20.0 sentencepiece transformers
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
# git clone https://github.com/xinntao/Real-ESRGAN.git
cd Real-ESRGAN
pip install basicsr
pip install facexlib
pip install gfpgan
pip install -r requirements.txt
python setup.py develop
echo '--- input your cuda version ---(run nvidia-smi.exe to check)'
$name = Read-Host '11 or 12'
if ($name -eq '11'){
    pip install nvidia-cudnn-cu11==8.9.7.29
} elseif ($name -eq '12') {
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