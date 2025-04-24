import { ConfigService } from '@nestjs/config';
import { ThrottlerModule } from '@nestjs/throttler';
export const securityConfig = (configService: ConfigService) => {
  return ThrottlerModule.forRoot({
    throttlers: [
      {
        limit: configService.get<number>('THROTTLE_LIMIT') || 10, 
        ttl: configService.get<number>('THROTTLE_TTL') || 60, 
      },
    ],
  });
};

export const jwtConstants = {
    secret: process.env.JWT_SECRET || (() => {
        if (process.env.NODE_ENV === 'production') {
          throw new Error('JWT_SECRET must be set in production environment');
        }
        console.error('WARNING: JWT_SECRET not set! Using a random secret that will change on restart.');
        // Use dynamic import instead of require
        const crypto = globalThis.require('crypto');
       return crypto.randomBytes(32).toString('hex');
      })(),
  expiresIn: process.env.ACCESS_TOKEN_EXPIRATION || '3600s', 
};

export const corsOptions = {
  origin: [
    'http://localhost:3000',
    'https://revofarmers.app',
  ],
  credentials: true,
};
