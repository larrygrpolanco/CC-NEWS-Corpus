# Step-by-Step Guide: Extracting Brookings HTML from Common Crawl on AWS EC2 (us-east-1)

This guide is designed for users with minimal Linux experience. It uses the AWS Console (web GUI) wherever possible and provides clear, copy-paste commands for the few required terminal steps. You will extract HTML files from Common Crawl and transfer them to your computer or Google Drive.

---

## 1. Create an AWS Account (if you don't have one)

- Go to [https://aws.amazon.com/](https://aws.amazon.com/) and sign up.
- You will need a credit card (AWS has a free tier, but you may incur small charges for compute time and storage).

---

## 2. Launch an EC2 Instance in us-east-1 (N. Virginia)

**All steps below are done in the AWS Console (web browser):**

1. Log in to the AWS Console: [https://console.aws.amazon.com/](https://console.aws.amazon.com/)
2. Set region: In the top right, select `N. Virginia (us-east-1)`.
3. Go to EC2: Search for "EC2" in the services menu.
4. Click "Launch Instance".
   - Name: `brookings-html-extract`
   - Amazon Machine Image (AMI): **Ubuntu Server 22.04 LTS** (recommended for compatibility)
   - Instance type: **t3.medium** (recommended; free tier users can use t2.micro but it will be slow)
   - Key pair: Create a new key pair (RSA), download the `.pem` file, and keep it safe (you'll need it to connect).
   - Network settings: Allow SSH (port 22) from your IP only (for security).
   - Storage: 30 GB (default is fine).
   - Click "Launch Instance".

---

## 3. Connect to Your Instance

**You must use a terminal for this step.**

- In the EC2 dashboard, select your instance and click "Connect" for instructions.
- Example command (replace `KEY.pem` and `ec2-XX-XX-XX-XX.compute-1.amazonaws.com`):

  ```bash
  chmod 400 KEY.pem
  ssh -i KEY.pem ubuntu@ec2-XX-XX-XX-XX.compute-1.amazonaws.com
  ```

- If you prefer a GUI, you can use [MobaXterm](https://mobaxterm.mobatek.net/) (Windows) or [Termius](https://termius.com/) (Mac/Win/Linux) for a graphical SSH client.

---

## 4. Install Python and Dependencies

Once connected:

```bash
sudo apt update
sudo apt install -y python3 python3-pip
pip3 install warcio boto3
```

---

## 5. Configure AWS CLI (for S3 Access)

Install AWS CLI:

```bash
sudo apt install -y awscli
```

Configure it (follow prompts, use default region `us-east-1`):

```bash
aws configure
```

- You will need to create an **IAM user** in the AWS Console with "AmazonS3ReadOnlyAccess" permission.
- Generate Access Key ID and Secret Access Key for this user and enter them when prompted.

---

## 6. Upload Your Script and CSV

From your local machine, use `scp` to copy files:

```bash
scp -i KEY.pem html_extractor_s3.py ubuntu@ec2-XX-XX-XX-XX.compute-1.amazonaws.com:~
scp -i KEY.pem brookings_cdx_working_sample_truncated.csv ubuntu@ec2-XX-XX-XX-XX.compute-1.amazonaws.com:~
```

Or use `nano`/`vim` to create/edit files directly.

---

## 7. Run the Extraction Script

On the EC2 instance:

```bash
python3 html_extractor_s3.py
```

Extracted HTML files will appear in the `html_raw/` folder.

---

## 8. Download Results Back to Your Computer

From your local machine:

```bash
scp -i KEY.pem -r ubuntu@ec2-XX-XX-XX-XX.compute-1.amazonaws.com:~/html_raw .
```

---

## 9. Clean Up

- When finished, **terminate your EC2 instance** in the AWS Console to avoid charges.
- Delete any large files from the instance if you want to avoid S3/EBS storage charges.

---

## 10. Notes

- You do **not** need to throttle requests when using S3 from EC2 in us-east-1.
- This guide uses the most beginner-friendly, reliable options (Ubuntu, on-demand instance, no spot pricing).
- If you have questions, search AWS docs or ask for help!

---
