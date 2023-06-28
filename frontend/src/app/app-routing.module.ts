import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import {MainPageComponent} from "./main-page/main-page.component";
import {LoginComponent} from "./login/login.component";
import {SharedComponent} from "./shared/shared-component";

const routes: Routes = [
  {path: '', component:LoginComponent},
  {path: 'main',component:MainPageComponent},
  {path: 'shared', component:SharedComponent},
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
