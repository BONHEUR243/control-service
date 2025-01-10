# control-service
This repository was done with intention to be presented as final year project to conclude 
a 3years program for advanced diploma in Electronics and telecommunication engineering.


This project presents the design and implementation of a smart access control system for exam 
rooms using ESP32, RFID technology, LCD display, and Wi-Fi connectivity integrated 
with a Django-based backend. The primary objective is to enhance security, rapidity and 
streamline the management of student access during examination periods. 
The system utilizes RFID cards for student identification, where each card is registered in a 
database hosted on a Django server. When a student scans their RFID card at the entrance, 
the NodeMCU retrieves the card data and sends a request to the Django server to verify the 
student's identity and access permissions. Based on the response, the system displays an 
appropriate message on the LCD screen, indicating whether access is granted or denied. 
Additionally, visual indicators such as green and red lamps provide immediate feedback on the 
access status. 


A website with “ulkcontrolservice.vercel.app” as domain name is deployed to ensure every 
student can see his/her personal details and a messaging system where he/she can claim or 
request access to administrators of school who manage access and individual details on their 
interface of the same website. This project addresses the need for a secure, fast, reliable, and 
user-friendly access control solution in educational institutions, aiming to prevent 
unauthorized entry and enhance the rapidity in accessing examination rooms. 
The implementation details, system architecture, and potential applications of the proposed 
solution are discussed, highlighting its effectiveness and scalability for broader use in similar 
scenarios. 
