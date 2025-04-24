import { Test, TestingModule } from '@nestjs/testing';
import { AuthController } from './controllers/auth.controller';
import { AuthService } from './services/auth.service';
import { RegisterDto } from './dto/register.dto';
import { LoginDto } from './dto/login.dto';

describe('AuthController', () => {
  let authController: AuthController;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [AuthController],
      providers: [AuthService],
    }).compile();

    authController = module.get<AuthController>(AuthController);
  });

  describe('register', () => {
    it('should register a new user', async () => {
      const registerDto: RegisterDto = {
        username: 'testuser',
        password: 'testpass',
      };
      const result = await authController.register(registerDto);
      expect(result).toHaveProperty('id');
      expect(result).toHaveProperty('username', 'testuser');
    });
  });

  describe('login', () => {
    it('should login a registered user', async () => {
      const registerDto: RegisterDto = {
        username: 'loginuser',
        password: 'loginpass',
      };
      await authController.register(registerDto);
      const loginDto: LoginDto = {
        username: 'loginuser',
        password: 'loginpass',
      };

      // Create a dummy request object with a session property
      const req: any = { session: {} };
      const result = await authController.login(loginDto);
      expect(result).toHaveProperty('id');
      expect(req.session.userId).toBe(result.user.id);
    });
  });
});
