import os
from reflex import App, Upload, ProgressBar, Text, Button, State, Store, events

# Create an upload directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Define application state
class AppState(State):
    uploaded_files = Store.list()  # Store for successfully uploaded files
    upload_progress = Store.dict()  # Store for tracking upload progress
    error_message = ""  # Store for errors

    @events.handler
    async def handle_upload(self, files):
        """Process file uploads."""
        for file in files:
            try:
                # Validate file type (e.g., only images and PDFs allowed)
                if not file.content_type.startswith(("image/", "application/pdf")):
                    raise ValueError(f"Unsupported file type: {file.content_type}")

                # Read the file
                content = await file.read()

                # Validate file size (max 10 MB)
                if len(content) > 10 * 1024 * 1024:  # 10 MB
                    raise ValueError(f"File {file.filename} is too large.")

                # Save file to the UPLOAD_DIR
                file_path = os.path.join(UPLOAD_DIR, file.filename)
                with open(file_path, "wb") as f:
                    f.write(content)

                # Update state with file metadata
                self.uploaded_files.append({
                    "name": file.filename,
                    "size": len(content),
                    "path": file_path,
                })

                # Simulate progress for demo purposes
                for i in range(1, 101):
                    self.upload_progress[file.filename] = i
                    await self.emit_update(delay=0.01)  # Simulate upload delay

            except Exception as e:
                # Handle errors gracefully
                self.error_message = f"Error uploading {file.filename}: {str(e)}"
                self.emit_update()
            finally:
                # Clear progress after completion
                if file.filename in self.upload_progress:
                    del self.upload_progress[file.filename]
                self.emit_update()

    @events.handler
    async def reset(self):
        """Reset the application state."""
        self.uploaded_files = []
        self.upload_progress = {}
        self.error_message = ""

# Define the application interface
class FileUploadApp(App):
    def build(self):
        return (
            Upload(
                "Drag and drop your files here or click to upload",
                multiple=True,
                accept="image/*,application/pdf",
                on_upload=AppState.handle_upload,
            )
            + ProgressBar(
                value=lambda state: list(state.upload_progress.values())[-1]
                if state.upload_progress
                else 0
            )
            + Text("Upload Progress", when=lambda state: bool(state.upload_progress))
            + Text(
                lambda state: f"Error: {state.error_message}",
                color="red",
                when=lambda state: bool(state.error_message),
            )
            + Text(
                lambda state: f"Uploaded Files: {', '.join(f['name'] for f in state.uploaded_files)}",
                when=lambda state: bool(state.uploaded_files),
            )
            + Button("Reset", on_click=AppState.reset)
        )

# Run the application
if __name__ == "__main__":
    FileUploadApp(state=AppState).run(debug=True)
