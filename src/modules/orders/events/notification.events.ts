export class NotificationSentEvent {
    constructor(
      public readonly type: 'email' | 'sms',
      public readonly to: string,
      public readonly message: string
    ) {}
  }