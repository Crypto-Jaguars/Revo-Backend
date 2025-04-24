/* eslint-disable prettier/prettier */
import { Module } from '@nestjs/common';
import { HttpModule } from '@nestjs/axios';
import { DashboardService } from './dashboard.service';

@Module({
  imports: [HttpModule],
  providers: [DashboardService],
  exports: [DashboardService],
})
export class DashboardModule {}
