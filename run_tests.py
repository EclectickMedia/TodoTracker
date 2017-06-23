import argparse
import io
import os
import platform
import smtplib
import subprocess
import sys
import time
import unittest

import log as l

parser = argparse.ArgumentParser()
parser.add_argument('-e', '--email', help='Flag this option to automatically '
                                          'send test results to the development'
                                          ' team. USAGE: -e USERNAME:PASSWORD')
parsed = parser.parse_args()


def output_system_info(log):
    pipe = subprocess.PIPE
    p = subprocess.Popen(['git', 'log', '--oneline', '-n 1'], stdout=pipe,
                         stderr=pipe)
    stdout, stderr = p.communicate()
    p.kill()

    log.writelines([
        '%s\n' % time.asctime(),
        'os.name: %s\n' % os.name,
        'platform.system: %s\n' % platform.system(),
        'platform.release: %s\n' % platform.release(),
        'commit: %s\n' % stdout.decode().split()[0],
        'Python version (via sys.version): %s\n\n' % sys.version
    ])


def run_tests(log, v=2):
    loader = unittest.TestLoader()
    # tests = loader.discover('.', '*.py')
    tests = loader.loadTestsFromName('TodoTracker')
    runner = unittest.TextTestRunner(stream=log, buffer=True, verbosity=v)
    log.write('Running TodoTracker tests\n')
    runner.run(tests)


def mail(log, uname, pword):
    mail = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    mail.ehlo()
    mail.login(uname, pword)
    try:
        mail.sendmail(uname, 'ariana.giroux@gmail.com', log)
    except smtplib.SMTPAuthenticationError as e:
        l.test_logger.critical('Failed to send email, got %s' % str(e))
        mail.close()

    mail.close()


log = io.StringIO()
output_system_info(log)
run_tests(log)

# UNCOMMENT TO ADD TO tests.log
# with open('logs/tests.log', 'a+') as test_log:
#     l.test_logger.info('Appending test results to tests log.')
#     test_log.writelines([line for line in log.getvalue()])

print(log.getvalue())
if parsed.email is not None:
    uname, pword = parsed.email.split(':')
    if not uname.count('@gmail.com'):
        l.test_logger.critical('Could not automatically send email, please '
                               'provide a valid gmail address and password.')
        sys.exit(2)

    with open('logs/tests.log') as f:
        log.write('tests log:\n')
        log.writelines([line for line in f])

    l.test_logger.info('Mailing results to development team.')
    mail(log, uname, pword)
    l.test_logger.info('Finished mailing results.')
