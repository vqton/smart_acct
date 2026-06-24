import { ApiProperty } from "@nestjs/swagger";
import { IsEmail, IsString, MinLength } from "class-validator";

export class RegisterDto {
  @ApiProperty({ example: "user@company.com" })
  @IsEmail()
  email!: string;

  @ApiProperty({ example: "P@ssw0rd!" })
  @IsString()
  @MinLength(6)
  password!: string;

  @ApiProperty({ example: "Nguyễn Văn A" })
  @IsString()
  displayName!: string;
}

export class LoginDto {
  @ApiProperty({ example: "user@company.com" })
  @IsEmail()
  email!: string;

  @ApiProperty({ example: "P@ssw0rd!" })
  @IsString()
  password!: string;
}
