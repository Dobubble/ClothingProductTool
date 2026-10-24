
#define MyAppName "ClothingProductTool"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "ClothingProductTool"
#define MyAppExeName "ClothingProductTool.exe"

[Setup]
; 正式发布后不要随意修改 AppId
AppId={{C7D49A82-4C2B-4E66-9F03-7A3C9C5D8412}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}

DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}

OutputDir=output
OutputBaseFilename=ClothingProductTool_Setup_1.0

Compression=lzma
SolidCompression=yes
WizardStyle=modern

ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

PrivilegesRequired=admin

UninstallDisplayName={#MyAppName} {#MyAppVersion}
UninstallDisplayIcon={app}\{#MyAppExeName}

DisableProgramGroupPage=yes
AllowNoIcons=no

CloseApplications=yes
RestartApplications=no

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "其他选项："; Flags: unchecked

[Files]
Source: "..\dist\ClothingProductTool\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\ClothingProductTool"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\ClothingProductTool"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "启动 ClothingProductTool"; Flags: nowait postinstall skipifsilent
