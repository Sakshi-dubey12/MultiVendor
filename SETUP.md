# How to Set Up and Run This Project

Welcome! Here's how you can get this project running on your computer, step by step.

1. **Install Docker Desktop**
   - Go to https://www.docker.com/products/docker-desktop/ and download Docker Desktop for Windows.
   - Run the installer and follow the instructions.
   - When it's done, restart your computer (this helps Docker work properly).
   - After restarting, open Docker Desktop and wait until you see the whale icon in your system tray (bottom right corner).

2. **Open a terminal window**
   - You can use PowerShell or Command Prompt.
   - Go to the folder where you have this project. For example:
     ```sh
     cd C:/Users/Asus/OneDrive/Desktop/MultiVendor
     ```

3. **Start the project**
   - In your terminal, type:
     ```sh
     docker compose up --build
     ```
   - This command will build and start all the parts of the project (the API, worker, vendor mocks, Redis, and MongoDB).
   - Wait until you see messages that say the services are running.

4. **Try it out!**
   - You can now use the example commands in the README file to send jobs to the API and check their status.
   - If you like, you can also use Postman or another tool to test the endpoints.

5. **When you're done**
   - To stop everything, go back to your terminal and press `Ctrl+C`.
   - If you want to clean up, type:
     ```sh
     docker compose down
     ```

