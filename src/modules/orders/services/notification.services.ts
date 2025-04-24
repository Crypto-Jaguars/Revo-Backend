import { Injectable, InternalServerErrorException } from '@nestjs/common';
import sgMail from '@sendgrid/mail';
import twilio from 'twilio';
import { notifyDto, EmailDto, SMSDto } from '../dtos/notification.dto';
import { orderStatusTemplate } from '../templates/email/email.templates';
import { orderStatusSMSTemplate } from '../templates/sms/sms.template';
import { ConfigService } from '@nestjs/config';
import { EventEmitter2 } from '@nestjs/event-emitter';
import { NotificationSentEvent } from '../events/notification.events';

@Injectable()
export class NotificationService {
  private twilioClient;

  constructor(
    private configService: ConfigService,
    private readonly eventEmitter: EventEmitter2,
  ) {
    sgMail.setApiKey(this.configService.get<string>('SENDGRID_API_KEY'));
    this.twilioClient = twilio(
      this.configService.get<string>('TWILIO_SID'),
      this.configService.get<string>('TWILIO_AUTH_TOKEN'),
    );
  }
  async emailsender(EmailDto: EmailDto) {
    await this.sendMail(EmailDto);
    this.eventEmitter.emit(
      'notification.sent',
      new NotificationSentEvent('email', EmailDto.to, EmailDto.html),
    );
  }

  async smsSender(SMSDto: SMSDto) {
    await this.sendSMS(SMSDto);
    this.eventEmitter.emit(
      'notification.sent',
      new NotificationSentEvent('sms', SMSDto.to, SMSDto.message),
    );
  }

  async sendStatusUpdateNotification(notifyDto: notifyDto) {
    const { email, phone, orderId, status } = notifyDto;

    const { subject, html } = orderStatusTemplate(email, orderId, status);
    const { message } = orderStatusSMSTemplate(phone, orderId, status);

    await this.emailsender({ to: email, subject, html });

    await this.smsSender({ to: phone, message });
  }

  private async sendMail(EmailDto: EmailDto) {
    try {
      await sgMail.send({
        to: EmailDto.to,
        from: this.configService.get<string>('SENDGRID_VERIFIED_SENDER'),
        subject: EmailDto.subject,
        html: EmailDto.html,
      });
    } catch (error) {
      throw new InternalServerErrorException('Failed to send email');
    }
  }

  private async sendSMS(SMSDto: SMSDto) {
    try {
      await this.twilioClient.messages.create({
        body: SMSDto.message,
        from: this.configService.get<string>('TWILIO_PHONE_NUMBER'),
        to: SMSDto.to,
      });

      
    } catch (error) {
      throw new InternalServerErrorException('Failed to send SMS');
    }
  }

  
}
