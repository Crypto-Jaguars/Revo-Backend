import {
  Controller,
  Post,
  Body,
  Req,
  UsePipes,
  ValidationPipe,
  Get,
  UseGuards,
} from '@nestjs/common';
import { AuthService } from '../services/auth.service';
import { RegisterDto } from '../dto/register.dto';
import { LoginDto } from '../dto/login.dto';
// import { Request } from 'express';
// import { promisify } from 'util';
import { JwtAuthGuard } from '../guards/jwt-auth.guard';
// import { User } from '../entities/user.entity';

@Controller('auth')
export class AuthController {
  constructor(private readonly authService: AuthService) {}

  // Registration endpoint
  @Post('register')
  @UsePipes(new ValidationPipe({ whitelist: true }))
  async register(@Body() registerDto: RegisterDto) {
    const user = await this.authService.register(
      registerDto.username,
      registerDto.password,
    );
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { password: _password, ...result } = user;
    return result;
  }

  // Login endpoint
  @Post('login')
  @UsePipes(new ValidationPipe({ whitelist: true }))
  async login(@Body() loginDto: LoginDto) {
    // No longer need session management with JWT
    return this.authService.login(loginDto.username, loginDto.password);
  }

  @Get('profile')
  @UseGuards(JwtAuthGuard)
  getProfile(@Req() req) {
    return req.user;
  }
  @Post('logout')
  async logout(): Promise<{ message: string }> {
    return { message: 'Logout successful. Please discard your token.' };
  }
}
