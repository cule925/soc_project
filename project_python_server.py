import socket
import struct
import numpy as np
import math
import cv2

# Server configuration
host = "10.0.0.10"  # Listen on all available network interfaces
port = 5001  # Replace with the port you want to listen on

# Define packet size variables
udp_packet_size = 1440
udp_metadata_size = 4
udp_data_size = udp_packet_size - udp_metadata_size

# Create a socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the host and port
server_socket.bind((host, port))

# Frame width and height
frame_width = 640
frame_height = 480
bytes_per_pixel = 2
total_frame_length = frame_width * frame_height * bytes_per_pixel

data_storage_length = math.ceil(total_frame_length / udp_data_size) * udp_data_size

print(f"Server listening on {host}:{port} , frame w:h {frame_width}x{frame_height}")

# Initialize an array to store the data
data_storage = bytearray(data_storage_length)

# Initialize an empty array for BGR888 data
bgr888_image = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)

while True:
  try:
    while True:
			
      # Receive data from the client
      data, address = server_socket.recvfrom(udp_packet_size)  # Receive up to udp_packet_size bytes

      if not data:
        print("No more data received from client.")
        break
      else:

        # Extract packet_id (first 4 bytes, assuming network byte order)
        packet_id = struct.unpack('!i', data[0:udp_metadata_size])[0]

        # Extract the rest of the data after the first 4 bytes
        payload = data[udp_metadata_size:]

        # Check for special packet_id indicating end of transmission
        if packet_id == -1:

          # Calculate the offset in the data_storage array
          offset = packet_id * udp_data_size
          end_offset = offset + len(payload)				# Last packet

          # Store the payload in the correct position of data_storage array
          data_storage[offset:end_offset] = payload

          # Convert the byte data to a numpy array
          bgr565_image = np.frombuffer(data_storage[:total_frame_length], dtype=np.uint16).reshape((frame_height, frame_width))

          # Convert into BGR888

          # Components from image
          red_component = (bgr565_image >> 11) & 0x1F
          green_component = (bgr565_image >> 5) & 0x3F
          blue_component = bgr565_image & 0x1F

          # Scale to 8 bits
          red_8bit = (red_component * 255 // 31).astype(np.uint8)
          green_8bit = (green_component * 255 // 63).astype(np.uint8)          
          blue_8bit = (blue_component * 255 // 31).astype(np.uint8)

          # Stack the color components
          bgr888_image = np.stack((blue_8bit, green_8bit, red_8bit), axis=-1)

          # Display the image using OpenCV
          cv2.imshow('Frame', bgr888_image)

          # If q is pressed then you must exit
          if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        else:

          # Calculate the offset in the data_storage array
          offset = packet_id * udp_data_size
          end_offset = offset + len(payload)				# Last packet

          # Store the payload in the correct position of data_storage array
          data_storage[offset:end_offset] = payload

  except KeyboardInterrupt:
    print("Server is closing.")
    break

# Close the server socket
cv2.destroyAllWindows()
server_socket.close()