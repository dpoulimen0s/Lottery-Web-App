# Imports
import copy

from flask import Blueprint, render_template, request, flash
from flask_login import current_user
from flask_login import login_required


from app import db, requires_roles
from models import Draw

# Config
lottery_blueprint = Blueprint('lottery', __name__, template_folder='templates')


# Views
# View lottery page
@lottery_blueprint.route('/lottery')
@login_required
@requires_roles('user')
def lottery():
    return render_template('lottery.html')


@lottery_blueprint.route('/add_draw', methods=['POST'])
@login_required
@requires_roles('user')
def add_draw():
    submitted_draw = ''
    for i in range(6):
        submitted_draw += request.form.get('no' + str(i + 1)) + ' '
    submitted_draw.strip()

    # Create an instance to take the current round.
    current_round = Draw.query.filter_by(win=True).first()

    # Create a new draw with the form data.
    new_draw = Draw(user_id=current_user.id,
                    draw=submitted_draw,
                    win=False,
                    round=current_round.round,
                    draw_key=current_user.draw_key)
    # TODO: update user_id [user_id=1 is a placeholder]-Done

    # Add the new draw to the database
    db.session.add(new_draw)
    db.session.commit()

    # Re-render lottery.page
    flash('Draw %s submitted.' % submitted_draw)
    return lottery()


# View all draws that have not been played
@lottery_blueprint.route('/view_draws', methods=['POST'])
@login_required
@requires_roles('user')
def view_draws():
    # Get all draws that have not been played [played=0]
    playable_draws = Draw.query.filter_by(played=False).where(Draw.user_id == current_user.id).all()
    # TODO: filter playable draws for current user - Done
    # creates a list of copied post objects which are independent of database.
    draw_copies = list(map(lambda x: copy.deepcopy(x), playable_draws))

    # empty list for decrypted copied post objects
    decrypted_draws = []

    # decrypt each copied post object and add it to decrypted_posts array.
    for d in draw_copies:
        d.view_draw(current_user.draw_key)
        decrypted_draws.append(d)

    if len(playable_draws) != 0:
        # Re-render lottery page with playable draws
        return render_template('lottery.html', playable_draws=decrypted_draws)
    else:
        flash('No playable draws.')
        return lottery()


# View lottery results
@lottery_blueprint.route('/check_draws', methods=['POST'])
@login_required
@requires_roles('user')
def check_draws():
    # Get played draws
    played_draws = Draw.query.filter_by(played=True).where(Draw.user_id == current_user.id).all()
    # TODO: filter played draws for current user - Done

    draw_copies = list(map(lambda x: copy.deepcopy(x), played_draws))

    # empty list for decrypted copied post objects
    decrypted_played_draws = []

    # decrypt each copied post object and add it to decrypted_posts array.
    for d in draw_copies:
        d.view_draw(current_user.draw_key)
        decrypted_played_draws.append(d)

    # If played draws exist
    if len(played_draws) != 0:
        return render_template('lottery.html', results=decrypted_played_draws, played=True)

    # If no played draws exist [all draw entries have been played therefore wait for next lottery round]
    else:
        flash("Next round of lottery yet to play. Check you have playable draws.")
        return lottery()


# Delete all played draws
@lottery_blueprint.route('/play_again', methods=['POST'])
@login_required
@requires_roles('user')
def play_again():
    delete_played = Draw.__table__.delete().where(
        Draw.user_id == current_user.id)
    # TODO: delete played draws for current user only - Done
    db.session.execute(delete_played)
    db.session.commit()

    flash("All played draws deleted.")
    return lottery()
