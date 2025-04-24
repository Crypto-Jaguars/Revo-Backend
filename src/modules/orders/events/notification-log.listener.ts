import { Injectable } from '@nestjs/common';
import { OnEvent } from '@nestjs/event-emitter';
import { NotificationSentEvent } from './notification.events';

@Injectable()
export class NotificationLogListener {
  @OnEvent('notification.sent', { async: true })
  handleNotificationSentEvent(event: NotificationSentEvent) {
    
    console.log(`[Notification Log] Type: ${event.type}, To: ${event.to}, Message: ${event.message}`);
    
    
  }
}
