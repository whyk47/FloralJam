# FloralJam

### Overview
FloralJam is a Django web application for organising and booking Floral Jamming events. 
Hosts can create and manage events and their participants. 
While users can register for events and receive automatic email conformation.

### Usage
[Link to Website](https://jfpzcpymy7.ap-southeast-1.awsapprunner.com/)
[Video Demo](https://youtu.be/Uqz5l15oKR4)

### Key Features
- Automated email service using stmp email backend.
- Supports Guest User sign ups.
- Web app is Dockerised and deployed on AWS AppRunner.
- Uses Amazon RDS Database backend.
- Uses Github Actions for CI/CD pipeline.

### File Structure
- views.py: Contains the Django views for handling various functionalities such as rendering pages, creating, editing, and deleting events, and registering and unregistering users.
- models.py: Defines the database models.
- templates/: Contains HTML templates and components for rendering different pages.
- services/: Contains the services delivering the main functionaility of the website, auth_service, email_service and event_service.

