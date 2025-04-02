
import { AuthService } from '../services/auth.service';
import { RegisterDto } from '../dto/register.dto';
import { LoginDto } from '../dto/login.dto';
import { User } from '../entities/user.entity';
import { ApiOperation, ApiTags, ApiResponse, ApiBody } from '@nestjs/swagger';
import { Controller, Post, Body} from '@nestjs/common';


@Controller('auth')
@ApiTags('auth') 
export class AuthController {
  constructor(private readonly authService: AuthService) {}

  @Post('register')
  @ApiOperation({ description: 'Registra un nuevo usuario en el sistema' })
  @ApiBody({ type: RegisterDto })
  @ApiResponse({ status: 201, description: 'Usuario registrado exitosamente' })
  @ApiResponse({ status: 400, description: 'Datos de registro inválidos' })
  register(@Body() registerDto: RegisterDto) {
    return this.authService.register(registerDto.username,registerDto.password);
  }

  @Post('login')
  @ApiOperation({ description: 'Inicia sesión para un usuario existente' })
  @ApiBody({ type: LoginDto })
  @ApiResponse({ status: 200, description: 'Inicio de sesión exitoso' })
  @ApiResponse({ status: 401, description: 'Credenciales inválidas' })
  login(@Body() loginDto: LoginDto) {
    return this.authService.login(loginDto.username,loginDto.password);
  }

}