import qrcode

student_name = input("Enter student name: ")
student_id = input("Enter student ID: ")

data = f"Name: {student_name}\nID: {student_id}"

qr = qrcode.make(data)
filename = f"{student_id}_{student_name}.png"
qr.save(filename)

print(f"✅ QR Code generated and saved as {filename}")

