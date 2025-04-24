import { ApiProperty } from '@nestjs/swagger';

export interface ApiResponse<T> {
    statusCode: number;
    message: string;
    data: T;
    timestamp: string;
}

export interface ApiErrorResponse {
    statusCode: number;
    message: string;
    error: string;
    timestamp: string;
}

export interface ApiVersion {
    version: string;
    status: 'active' | 'deprecated' | 'sunset';
    sunsetDate?: Date;
}

export class BaseResponseDto<T> {
    @ApiProperty({ example: 200 })
    statusCode: number;

    @ApiProperty({ example: 'Success' })
    message: string;

    @ApiProperty()
    data: T;

    @ApiProperty({ example: '2024-03-26T00:00:00.000Z' })
    timestamp: string;
}

export class BaseErrorResponseDto {
    @ApiProperty({ example: 400 })
    statusCode: number;

    @ApiProperty({ example: 'Bad Request' })
    message: string;

    @ApiProperty({ example: 'ValidationError' })
    error: string;

    @ApiProperty({ example: '2024-03-26T00:00:00.000Z' })
    timestamp: string;
} 