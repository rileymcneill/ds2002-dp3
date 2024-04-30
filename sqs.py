import boto3
from botocore.exceptions import ClientError

url = "https://sqs.us-east-1.amazonaws.com/440848399208/mqt3uz"
region = "us-east-1"

try:
    sqs = boto3.client('sqs', region_name=region)
except NoRegionError:
    print("Error: You must specify a region.")
    exit(1)

def delete_message(handle):
    try:
        sqs.delete_message(
            QueueUrl=url,
            ReceiptHandle=handle
        )
        print("Message deleted")
    except ClientError as e:
        print(e.response['Error']['Message'])

def get_messages():
    try:
        response = sqs.receive_message(
            QueueUrl=url,
            AttributeNames=['All'],
            MaxNumberOfMessages=10,
            MessageAttributeNames=['All']
        )
        if "Messages" in response:
            messages = []
            for msg in response['Messages']:
                order = int(msg['MessageAttributes']['order']['StringValue'])
                word = msg['MessageAttributes']['word']['StringValue']
                handle = msg['ReceiptHandle']
                messages.append({"order": order, "word": word, "handle": handle})
            return messages
        else:
            print("No messages in the queue")
            return []
    except ClientError as e:
        print(e.response['Error']['Message'])

def reassemble_phrase(messages):
    messages.sort(key=lambda x: x['order'])
    phrase = ' '.join(msg['word'] for msg in messages)
    return phrase

if __name__ == "__main__":
    messages = get_messages()
    if messages:
        print("Messages retrieved from SQS queue:")
        for msg in messages:
            print(f"Order: {msg['order']}, Word: {msg['word']}")
        
        phrase = reassemble_phrase(messages)
        print("\nReassembled phrase:", phrase)
        
        with open("phrase.txt", "w") as file:
            file.write(phrase)
            
        for msg in messages:
            delete_message(msg['handle'])
    else:
        print("No messages to process")