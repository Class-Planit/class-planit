        invitation_match = studentInvitation.objects.get(id=prev.id)
        invite_email = invitation_match.email

        if invite_email:
            try:
                message = Mail(
                    from_email='welcome@classplanit.co',
                    to_emails=invite_email,
                    subject="You're Invited",
                    html_content= get_template('dashboard/student_invite_email.html').render({'invitation_match': invitation_match))
            except Exception as e:
                pass
        try:
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            pass
        return redirect('thank_you', user_id=user_id)
    else:
        return redirect('registration_full', retry=True)