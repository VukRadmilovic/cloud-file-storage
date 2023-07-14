# Cloud file storage and management web app

## Tech Stack
- AWS 
- Serverless Framework
- Python
- Angular

## Description
Cloud computing web application designed for storing, managing, and organizing photos, videos and other files. This application offers a user-friendly interface and leverages AWS cloud services with a serverless architecture.

### Key Features
- User Registration and Authentication: Easily create an account and log in securely with your username and password to access all the application functionalities.
- Content Upload: Upload various types of content, including photos, videos, audio files, and documents (e.g., PDF, HTML, DOCX). Capture essential information such as filename, file type, file size, creation time, and last modification time. Add custom details such as descriptions and tags to enhance organization and search capabilities.
- Content Access: View and manage all your uploaded content.
- Content Modification: Edit the content you own, including the media files and associated information.
- Content Deletion: Delete your uploaded content effortlessly.
- Albums: Create personalized photo albums to organize your content. Easily move existing content into albums or add new content directly.
- Content Sharing: Share your content with other users. Choose whether to share at the content level or the album level. Users with shared access can view and download the content but cannot modify or delete it.
- Content Download: Download content you have access to

### System Architecture and Technologies
The project is built on a serverless architecture utilizing AWS Lambda functions written in Python. The Serverless Framework is used for infrastructure as code, simplifying the deployment and management of AWS services. AWS Cognito handles user authentication and provides a secure login system. Angular is used to provide the frontend of the application.

## How to Run
1. Clone the repository
2. Navigate to the project directory
3. Install dependencies and deploy the application using the Serverless Framework:
```
serverless deploy
```
4. Navigate to the frontend directory
5. Install frontend dependencies:
```
npm install
```
6. Start the frontend development server:
```
ng serve
```
Open your web browser and visit http://localhost:4200 to access the application.

Note: Before running the serverless deployment command, ensure that you have set up access keys on your PC to interact with AWS services. These access keys will be used during the deployment process to authenticate and authorize the necessary actions.
The deployment process may take a few minutes to complete. Once it finishes, you will receive information about the deployed resources, including the endpoints to access your application.
