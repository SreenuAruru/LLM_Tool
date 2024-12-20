### Frontend 

![image](https://github.com/user-attachments/assets/1b316d2e-387f-4763-97c9-e0a8811e1290) 
Here runs the frontend with above provided image commands and get than get “build” file like above image

### Backend: -

![image](https://github.com/user-attachments/assets/5f8d6fb2-e646-4080-8345-1e445c26057d)

1. maintain ‘.env’ file for external storage option.
2. maintain ‘requirement.txt’ file for install all python package at a time by using above commands.
3. Access application (main.exe) file in backend/dist folder.
4. coming to the ‘main.spec’ file will be contains build and dist related configuration.
5. when you open backend application (main.exe) below image like.
![image](https://github.com/user-attachments/assets/3a0c5b22-08b3-4315-9487-d7bd8a554f62)

### Electron: -

![image](https://github.com/user-attachments/assets/8898f3b3-639c-4c83-8d63-62435a8cfa8d)

1. Electron is one of Java script frame work for creating an application installer like dist.
2. This folder I implement code ‘main.js’ and ‘package.json’ files.
3. Electron dist folder provide frontend application (llm-tool.exe) file.
4. Create “frontend” folder in “dist/llm-tool-win32-x64/resources” folder and add frontend ”build” folder by follow below image.
![image](https://github.com/user-attachments/assets/b56e066d-b932-4d5a-9c94-6fce918a62ca)
 
6. Must and should followed the files path and add dots in frontend/build/“index.html” it will be path build in electron folder access.
![image](https://github.com/user-attachments/assets/a580a18b-a2db-4e15-82b0-5511f08b858a)
 
8. When you open frontend application (llm-tool.exe) file in electron folder and its open frontend application like below image.
![image](https://github.com/user-attachments/assets/35338cb0-d938-402c-826f-aedf51f24680)
 
 Commands: -
### React commands
1. npm install = for install frontend package.json node_modules
2. npm start = starting frontend server
3. npm run build = build frontend file
### Python commands
1. pip install -r requirements.txt = if have requirement.txt file in python directly use this command to install packages
2. uvicorn main:app --reload = for start the backend server
3. pyinstaller --onefile main.py = for ""automatic"" build build and dist files created
4. pyinstaller main.spec - we have already ""manual"" "main.spec" file run this command
### Database & Tables
MYSQL: -
CREATE SCHEMA `iadb` ;
use iadb;

CREATE TABLE model_selection (
id INT AUTO_INCREMENT PRIMARY KEY,
ai_model VARCHAR(255) NOT NULL,
model_api_key VARCHAR(255) NOT NULL
);

may be database automatically created so no needed to create any databases and schemas

### Electron Commands
1. npm install = for install electron package.json node_modules
2. npm run package = for build electron dist on electron folder
