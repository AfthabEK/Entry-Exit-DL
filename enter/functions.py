from .models import record
from .models import student as studentrec
from datetime import date, timedelta, datetime
import asyncio
import websockets
import socket
import time
import threading
from asgiref.sync import sync_to_async

student_id = None
record_queue = asyncio.Queue()
library_message_queue = asyncio.Queue()
ws_conns = set()

def isnine(s):
    if len(s)==9 and s[0].isalpha() and s[1:7].isdigit() and s[7:9].isalpha():
        return True
    else:
        return False
def isfour(s):
    if len(s)==4 and s[0:3].isdigit():
        return True
    else:
        return False

@sync_to_async
def read_data():
    readerIP='192.168.230.16'
    readerPort=100
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.SOL_TCP)
        s.settimeout(2)
        s.connect((readerIP, readerPort))
    except Exception as e:
        raise Exception('NetworkError: Socket creation failed.')

    #print("Sending Read request.")
    cmd = bytearray([10, 255, 2, 128, 117])
    s.send(cmd)

    # Reading response
    out = s.recv(2048)
    cnt = out[5]
    #print("Response: " + " ".join("%02x" % b for b in out))

    #print("Sending get tag data request.")
    cmd = bytearray([10, 255, 3, 65, 16, 163])
    s.send(cmd)

    # Reading response
    out = s.recv(2048)
    #print("Response: " + " ".join("%02x" % b for b in out))
    if out[4] > 1:
        raise Exception("WARNING: More than one tags in range!!!")
    elif out[4] == 0:
        raise Exception("WARNING: No tags in range!!!")
    out = out[7:7+12][::-1]
    if out[1] == 0x9e:
        raise Exception("WARNING: Attempted to read empty tag.")
    out = out.decode()
    out = ''.join([c if ord(c) != 0 else '' for c in out])

    #print(out)
    return out

async def reader_daemon():
    global student_id
    old_student_id = None
    
    while True:
        start_time = time.time()
        try:
            data = await read_data()
            if data:
                student_id = data[1:]
            else:
                student_id = None
        except:
            pass
        if time.time() - start_time < 0.5:
            # so that the reader doesn't get 'stressed' out
            await asyncio.sleep(0.5 - (time.time()-start_time))
        
        if old_student_id != student_id and student_id is not None:
            await record_queue.put(student_id)
            old_student_id = student_id

@sync_to_async
def insert_record(student_id):
    today = date.today()
    yesterday = datetime.now().date() - timedelta(days=2)
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    try:
            # Check if student_id is in the correct format (e.g., B200719CS)
        if not( isnine(student_id) or isfour(student_id) ):
                message = '<span class="text-center alert alert-danger">Error: Invalid roll number format. Please try again.</span>'
        else:
            student = record.objects.get(rollno=student_id, status='IN')
            if student.status == 'IN':
                student.exittime = current_time
                student.status = 'OUT'
                student.save()
                exit_hrs,exit_mins,exit_sec =map(int,student.exittime.split(':'))
                exit_time=3600*exit_hrs + 60*exit_mins + exit_sec
                entry_hrs,entry_mins,entry_sec = map(int,student.entrytime.strftime("%H:%M:%S").split(':'))
                entry_time=3600*entry_hrs + 60*entry_mins + entry_sec
                duration=exit_time - entry_time
                hours = duration//3600
                mins = (duration%3600)//60
                message = f'<span class="text-center alert alert-warning">Thank you for visiting NITC Library, you have spent {hours} Hrs {mins} Mins here today</span>'
            else:
                    # Create a new record for a student entering
                record.objects.create(rollno=student_id, entrytime=current_time, date=today)
                try:
                    student_name = studentrec.objects.get(rollno=student_id)
                    message = f'<span class="text-center alert alert-success">{student_name} has entered the library at {current_time}</span>'
                except:
                    if(len(student_id)==9):
                        message = f'<span class="text-center alert alert-success">Student with roll number {student_id} has entered the library at {current_time}</span>'
                    else:
                        message = f'<span class="text-center alert alert-success">Staff with ID {student_id} has entered the library at {current_time}</span>'
    except record.DoesNotExist:
            # Create a new record for a student entering
        record.objects.create(rollno=student_id, entrytime=current_time, date=today)
        try:
            student_name = studentrec.objects.get(rollno=student_id)
            message = f'<span class="text-center alert alert-success">{student_name} has entered the library at {current_time}</span>'
        except:
            if(len(student_id)==9):

                message = f'<span class="text-center alert alert-success">Student with roll number {student_id} has entered the library at {current_time}</span>'
            else:
                message = f'<span class="text-center alert alert-success">Staff with ID {student_id} has entered the library at {current_time}</span>'
    return message
            
async def record_queue_handler():
    while True:
        student_id = await record_queue.get()
        student_id = student_id.upper()
        message = await insert_record(student_id)
        await library_message_queue.put(message)

async def library_message_queue_handler():
    while True:
        message = await library_message_queue.get()

        ws_conns_ = set(ws_conns)
        for conn in ws_conns_:
            try:
                await conn.send(message)
            except Exception as e:
                ws_conns.remove(conn)

async def reader_ws_handler(websocket):
    try:
        ws_conns.add(websocket)
        while True:
            student_id = str(await websocket.recv()).strip()
            if student_id == "":
                try:
                    reader_data = await read_data()
                    if reader_data:
                        await record_queue.put(reader_data[1:])
                        continue
                except:
                    await websocket.send('<span class="text-center alert alert-danger">Error: Failed to read data from the reader. Please try again.</span>')
                    continue
            await record_queue.put(student_id)
    except Exception as e:
        pass

async def reader_ws_server():
    async with websockets.serve(reader_ws_handler, "localhost", 8765):
        await asyncio.Future()

async def async_bg_jobs():
    await asyncio.gather(reader_ws_server(), record_queue_handler(), library_message_queue_handler(), reader_daemon())
def async_bg_jobs_wrapper():
    asyncio.run(async_bg_jobs())

async_bg_jobs_thread = threading.Thread(target=async_bg_jobs_wrapper)
async_bg_jobs_thread.daemon = True
async_bg_jobs_thread.start()
