import sys
from time import sleep

import pygame
from bullet import Bullet
from alien import Alien
def check_keydown_events(event,ai_settings,screen,red3,bullets):
    """respond to key presses"""
    if event.key==pygame.K_RIGHT:
        red3.moving_right=True
    elif event.key==pygame.K_LEFT:
        red3.moving_left=True
    elif event.key==pygame.K_SPACE:   
     
        #create a new bullet and add it to the bellet group.
        if len(bullets) <ai_settings.bullet_allowed:
          new_bullet=Bullet(ai_settings,screen,red3)
          bullets.add(new_bullet)
    elif event.key==pygame.K_q:
        sys.exit()       
def update_bullets(ai_settings,screen,stats,sb,red3,aliens,bullets):
    """update position of bullet and get rid of old bullets."""
    #update bullet position
    bullets.update()

    #get rid of bullets that disappeared
    for bullet in bullets.copy():
        if bullet.rect.bottom <=0:
         bullets.remove(bullet)

    #Check for any bullet that have hit the alien
    #if so get rid of the bullet and the alien
    check_bullet_alien_collisions(ai_settings,screen,stats,sb,red3,aliens,bullets)

def check_bullet_alien_collisions(ai_settings,screen,stats,sb,red3,aliens,bullets):
    """Respond to bullet alien collision"""
    #remove any bullet and alien that have collided    
    collisions=pygame.sprite.groupcollide(bullets,aliens,True,True)
    if collisions:
        for aliens in collisions.values():
           stats.score +=ai_settings.alien_points * len(aliens)
           sb.prep_score()
        check_high_scores(stats,sb)   


    if len(aliens)==0:
        #If the entire fleet is destroyed start a new level

        bullets.empty()
        ai_settings.increase_speed()
        #increase level
        stats.level += 1
        sb.prep_level()
        create_fleet(ai_settings,screen,red3,aliens)                 

def check_keyup_events(event,red3):
    """respond to key release"""
    if event.key==pygame.K_RIGHT:
        red3.moving_right=False
    elif event.key==pygame.K_LEFT:
        red3.moving_left=False                
def check_events(ai_settings,screen,stats,sb,play_button,red3,aliens,bullets):
    """respond to key presses and mouse event"""
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
          sys.exit()
        elif event.type==pygame.KEYDOWN:
            check_keydown_events(event,ai_settings,screen,red3,bullets)
        elif event.type==pygame.KEYUP:
            check_keyup_events(event,red3)

        elif event.type==pygame.MOUSEBUTTONDOWN:
            mouse_x,mouse_y=pygame.mouse.get_pos()
            check_play_button(ai_settings,screen,stats,sb,play_button,red3,aliens,bullets,mouse_x,mouse_y)

def check_play_button(ai_settings,screen,stats,sb,play_button,red3,aliens,bullets,mouse_x,mouse_y):
    """Start a new game when the player click play"""
    button_clicked=play_button.rect.collidepoint(mouse_x,mouse_y)
    if button_clicked and not stats.game_active:
        #reset the game settings
        ai_settings.initialize_dynamic_settings()
        #Hide the mouse cursor.
        pygame.mouse.set_visible(False)
        #Reset the game statistic.
        stats.reset_stats()
        stats.game_active=True
        #reset the scoreboard images
        sb.prep_score()
        sb.prep_high_score()
        sb.prep_level()
        sb.prep_red3s() 
        #Empty the list of aliens and bullets

        aliens.empty()
        bullets.empty()

        #Create a new fleet and center the ship.
        create_fleet(ai_settings,screen,red3,aliens)
        red3.center_red3()               
                 
          
def update_screen(ai_settings,screen,stats,sb,red3,aliens,bullets,play_button):
    """update image on the screen and flip to the new screen"""
    #redraw the screen during each pass through the loop
    screen.fill(ai_settings.bg_color)
    #Redrwa all bullets behind red3 and aliens
    for bullet in bullets.sprites():
        bullet.draw_bullet()
    red3.blitme()
    aliens.draw(screen)
    #Draw the score information
    sb.show_score()

    #Draw the game button if the game is inactive
    if not stats.game_active:
        play_button.draw_button()

    #make the recent screen visible
    pygame.display.flip()

def get_number_aliens_x(ai_settings,alien_width):
    """Determine the number of alien that fit in a row"""
    available_space_x=ai_settings.screen_width-2*alien_width
    number_alien_x=int(available_space_x /(2*alien_width))
    return number_alien_x

def get_number_rows(ai_settings,red3_height,alien_height):
    """Determine the number of rows of alien that fits on the screen"""
    available_space_y=(ai_settings.screen_height-(3*alien_height)-red3_height)
    number_rows=int(available_space_y /(2*alien_height))
    return number_rows    

def create_alien(ai_settings,screen,aliens,alien_number,row_number):
    """Create an alien and place it in the row"""
    alien=Alien(ai_settings,screen,)
    alien_width=alien.rect.width 
    alien.x=alien_width+2*alien_width*alien_number
    alien.rect.x=alien.x
    alien.rect.y=alien.rect.height + 2 *alien.rect.height *row_number
    aliens.add(alien)  


def create_fleet(ai_settings,screen, red3,aliens):
    """Create a full fleets of Aliens"""
    #Create an alien and find the number of Aliens in a row
    #spacing between each alien is equal to one alien width

    alien=Alien(ai_settings,screen,)
    number_aliens_x=get_number_aliens_x(ai_settings,alien.rect.width)
    number_rows=get_number_rows(ai_settings,red3.rect.height,alien.rect.height)
     #Create the first row of Aliens
    for row_number in range(number_rows):
        for alien_number in range(number_aliens_x):
          create_alien(ai_settings,screen,aliens,alien_number,row_number)

def check_fleet_edges(ai_settings,aliens):
    """respond appropriately if any alien have reached the edge"""
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(ai_settings,aliens)
            break
def change_fleet_direction(ai_settings,aliens):
    """Drop the entire fleet and change the fleet direction"""
    for alien in aliens.sprites():
        alien.rect.y +=ai_settings.fleet_drop_speed
    ai_settings.fleet_direction *= -1

def rocket_hit(ai_settings,stats,sb,screen,red3,aliens,bullets):
    """Respond to rocket being hit by an alien"""
    if stats.red3s_left > 0:
      #Decrement rocket_left.
       stats.red3s_left -= 1
       #Update scoreboard
       sb.prep_red3s()

       #Empty the list of aliens and bullets.
       aliens.empty()
       bullets.empty()

      #create a new fleet and center the ship
       create_fleet(ai_settings,screen,red3,aliens)
       red3.center_red3()

       #pause
       sleep(0.1)
    else:
        stats.game_active=False
        pygame.mouse.set_visible(True)    

def check_aliens_bottom(ai_settings,stats,sb,screen,red3,aliens,bullets):
    """Check if any alien has reached the bottom of the screen"""
    screen_rect=screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom >=screen_rect.bottom:
            #Treat the same as if the ship got hit
            rocket_hit(ai_settings,stats,sb,screen,red3,aliens,bullets)
            break                              

def update_aliens(ai_settings,stats,sb,screen,red3,aliens,bullets):
    """check if the fleet is at the edge,and then
    update the position of aliens in the fleet"""
    check_fleet_edges(ai_settings,aliens)
    aliens.update()        

    #look for alien sheep collision
    if pygame.sprite.spritecollideany(red3,aliens):
        rocket_hit(ai_settings,stats,sb,screen,red3,aliens,bullets)
        print("Rocket down!")
    #Look for aliens hitting the bottom of the screen
    check_aliens_bottom(ai_settings,stats,sb,screen,red3,aliens,bullets)

def check_high_scores(stats,sb):
    """Check to see if there is a new high score"""
    if stats.score>stats.high_score:
        stats.high_score=stats.score
        sb.prep_high_score()        