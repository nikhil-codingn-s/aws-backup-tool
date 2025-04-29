from flask import Flask, request, jsonify
import boto3
import datetime
import os

app = Flask(__name__)

API_KEY = "my-secret-token"

session = boto3.Session()
ec2 = session.client('ec2', region_name='us-east-1')

@app.route('/')
def index():
    return "AWS EC2 Backup Tool is Running!"

@app.route('/buckets')
def list_buckets():
    s3 = boto3.client('s3')
    buckets = s3.list_buckets()
    bucket_names = [b['Name'] for b in buckets['Buckets']]
    return f"Available Buckets: {', '.join(bucket_names)}"

@app.route('/backup', methods=['POST'])
def backup_instance():
    if request.headers.get('X-API-KEY') != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    instance_id = data.get('instance_id')

    if not instance_id:
        return jsonify({"error": "Missing instance_id"}), 400

    timestamp = datetime.datetime.utcnow().strftime('%Y%m%d-%H%M%S')
    ami_name = f"Backup-{instance_id}-{timestamp}"

    try:
        response = ec2.create_image(
            InstanceId=instance_id,
            Name=ami_name,
            Description='Automated backup',
            NoReboot=True
        )
        return jsonify({
            "message": "✅ Backup initiated successfully!",
            "image_id": response['ImageId'],
            "ami_name": ami_name
        }), 200
    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

