# plugin for USERGE-X by @Kakashi_HTK(tg)/@ashwinstr(gh)
# please ask before porting to other bots, thank you


import http.client
import json
import os

from userge import Config, Message, userge
from userge.helpers import time_date_diff
from userge.utils import post_to_telegraph as pt

FOOTBALL_API = os.environ.get("FOOTBALL_API")
FOOTBALL_UTC_TIME = os.environ.get("FOOTBALL_UTC_TIME")


@userge.on_cmd(
    "fbc",
    about={
        "header": "get competition/league codes",
        "flags": {"-j": "get entire json format"},
        "usage": "{tr}fbc",
    },
)
async def fb_leauges_(message: Message):
    """get competition/league codes"""
    if not FOOTBALL_API:
        await message.edit(
            "API token as <code>FOOTBALL_API<code> needed, get it from football-data.org...",
            del_in=5,
        )
        return
    await message.edit("<code>Fetching available competitions...<code>")

    try:
        connection = http.client.HTTPConnection("api.football-data.org")
        headers = {"X-Auth-Token": FOOTBALL_API}
        connection.request("GET", f"/v2/competitions", None, headers)
        response = json.loads(connection.getresponse().read().decode())
    except Exception as e:
        await message.err(e, del_in=5)
        return

    if "-j" in message.flags:
        json_ = json.dumps(response, indent=4)
        await message.edit_or_send_as_file(json_)
        return
    leagues_ = "The <b>leagues</b> available in the <b>API</b>: [<b>{}</b>]\n\n"
    total_ = 0
    try:
        comps_ = response["competitions"]
    except BaseException:
        await message.err("No competitions available as for now.", del_in=5)
        return
    for comp in comps_:
        if comp["plan"] == "TIER_ONE":
            try:
                name_ = comp["name"]
                code_ = comp["code"]
                area_ = comp["area"]["name"]
            except Exception as e:
                await message.edit(e, del_in=5)
                return
            total_ += 1
            leagues_ += (
                f"[{total_}] <b>{name_}</b> <i>({area_})</i> - <code>{code_}</code>\n"
            )
    await message.edit_or_send_as_file(leagues_.format(total_))


@userge.on_cmd(
    "fbt",
    about={
        "header": "get team codes/IDs",
        "flags": {"-j": "get entire json format"},
        "usage": "{tr}fbteams [league code]",
    },
)
async def fb_teams_(message: Message):
    """get team codes/IDs"""
    if not FOOTBALL_API:
        await message.edit(
            "API token as <code>FOOTBALL_API<code> needed, get it from football-data.org...",
            del_in=5,
        )
        return
    league_ = message.filter_input_str
    if not league_:
        await message.edit("Input not found, give competition code...", del_in=5)
        return
    league_ = league_.upper()
    await message.edit("<code>Checking league code...<code>")

    try:
        connection = http.client.HTTPConnection("api.football-data.org")
        headers = {"X-Auth-Token": FOOTBALL_API}
        connection.request("GET", f"/v2/competitions/{league_}/teams", None, headers)
        response = json.loads(connection.getresponse().read().decode())
    except BaseException:
        await message.edit(
            f"Wrong code, see <code>{Config.CMD_TRIGGER}help fbt</code> for competition codes.",
            del_in=5,
        )
        return

    if "-j" in message.flags:
        json_ = json.dumps(response, indent=4)
        await message.edit_or_send_as_file(json_)
        return
    season_ = response["season"]
    start_ = (season_["startDate"]).split("-")[0]
    end_ = (season_["endDate"]).split("-")[0][2:]
    if start_[2:] == end_:
        start_end = start_
    else:
        start_end = f"{start_}/{end_}"
    lname = response["competition"]["name"]
    nation = response["competition"]["area"]["name"]
    team_list = (
        f"<b>Teams</b> competing in <b>{lname} <i>({nation})</i> ({league_})</b> this season <i>({start_end})</i>:"
        + " [<b>{}</b>]<br>"
    )
    total_ = 0
    try:
        teams_ = response["teams"]
    except BaseException:
        await message.edit("`Couldn't find any team...`", del_in=5)
        return
    for team in teams_:
        try:
            id_ = team["id"]
            tname_ = team["name"]
        except Exception as e:
            await message.err(e, del_in=5)
            return
        total_ += 1
        if league_ == ("CL" or "EC" or "CLI" or "WC"):
            nation_ = team["area"]["name"]
            nation_ = f" <i>({nation_})</i>"
        else:
            nation_ = ""
        team_list += f"[{total_}] <code>{id_}</code> <b>{tname_}</b>{nation_}<br>"
    team_list = team_list.format(total_)
    link_ = pt(f"Teams in {lname} for season {start_end}", team_list)
    await message.edit(
        f"Teams in <b>{lname}</b> for season <i>({start_end})</i> are <a href='{link_}'><b>HERE</b></a>"
    )


@userge.on_cmd(
    "fbsc",
    about={
        "header": "get team schedule",
        "flags": {"-j": "get entire json format"},
        "usage": "{tr}fbteams [team ID]",
    },
)
async def fb_sched_(message: Message):
    """get team schedule"""
    if not FOOTBALL_API:
        await message.edit(
            "API token as <code>FOOTBALL_API<code> needed, get it from football-data.org...",
            del_in=5,
        )
        return
    id_ = message.filtered_input_str
    if not id_:
        id_ = "66"
    await message.edit("<code>Checking team ID...<code>")
    if not id_.isdigit():
        await message.edit("Enter a proper team ID...", del_in=5)
        return

    try:
        connection = http.client.HTTPConnection("api.football-data.org")
        headers = {"X-Auth-Token": FOOTBALL_API}
        connection.request("GET", f"/v2/teams/{id_}/matches", None, headers)
        response = json.loads(connection.getresponse().read().decode())
    except BaseException:
        await message.edit(
            f"Wrong code, see <code>{Config.CMD_TRIGGER}help fbsc</code> for competition codes.",
            del_in=5,
        )
        return

    if "-j" in message.flags:
        json_ = json.dumps(response, indent=4)
        await message.edit_or_send_as_file(json_)
        return
    matches_ = response["matches"]
    season_ = matches_[0]["season"]
    start_ = (season_["startDate"]).split("-")[0]
    end_ = (season_["endDate"]).split("-")[0][2:]
    if start_[2:] == end_:
        start_end = start_
    else:
        start_end = f"{start_}/{end_}"
    if matches_[0]["homeTeam"]["id"] == int(id_):
        the_team = matches_[0]["homeTeam"]["name"]
    else:
        the_team = matches_[0]["awayTeam"]["name"]
    matches_sch = (
        f"Matches for <b>{the_team}</b> this season <i>({start_end})</i>:<br><br>"
    )
    for match_ in matches_:
        match_id = match_["id"]
        comp_n = match_["competition"]["name"]
        home_t = match_["homeTeam"]["name"]
        away_t = match_["awayTeam"]["name"]
        md = match_["matchday"]
        if match_["status"] == "FINISHED":
            finished = True
            score = match_["score"]["fullTime"]
            h_score = score["homeTeam"]
            a_score = score["awayTeam"]
            if h_score > a_score:
                h_score = f"<b>{h_score}</b>"
                home_t = f"<b>{home_t}</b>"
            elif h_score < a_score:
                a_score = f"<b>{a_score}</b>"
                away_t = f"<b>{away_t}</b>"
            else:
                pass
        else:
            finished = False
            h_score = ""
            a_score = ""
        sche_ = match_["utcDate"]
        date_ = sche_.split("T")[0]
        date_ = date_.split("-")
        date_y = int(date_[0])
        date_m = int(date_[1])
        date_d = int(date_[2])
        time_ = sche_.split("T")[1]
        time_h = time_.split(":")[0]
        time_h = int(time_h)
        time_m = time_.split(":")[1]
        time_m = int(time_m)
        if FOOTBALL_UTC_TIME:
            differ = FOOTBALL_UTC_TIME
        else:
            differ = "+5:30"
        t_d_ = time_date_diff(
            year=date_y,
            month=date_m,
            date=date_d,
            hour=time_h,
            minute=time_m,
            diff=differ,
        )
        matches_sch += f"• <b>Competetion:</b> {comp_n} <b>Match day:</b> <i>{md}</i> <b>Match ID:</b> <code>{match_id}</code><br>"
        if finished:
            matches_sch += f"{h_score} - {home_t}<br>" f"{a_score} - {away_t}<br>"
        else:
            if home_t == the_team:
                home_t = f"<b>{home_t}</b>"
            else:
                away_t = f"<b>{away_t}</b>"
            matches_sch += f"{home_t}<br>" f"{away_t}<br>"
        matches_sch += f"{t_d_['date']}/{t_d_['month']}/{t_d_['year']} at {t_d_['hour']}:{t_d_['min']} {t_d_['stamp']} UTC{differ}<br><br>"
    link_ = pt(f"Matches for {the_team} this season.", matches_sch)
    await message.edit(
        f"Schedule for <b>{the_team}</b> is <a href='{link_}'><b>HERE</b></a>"
    )


@userge.on_cmd(
    "fbfix",
    about={
        "header": "get fixtures",
        "flags": {"-j": "get entire json format"},
        "usage": "{tr}fbfix [league code] [matchDay (optional)]",
    },
)
async def fb_fixtures_(message: Message):
    """get fixtures"""
    if not FOOTBALL_API:
        await message.edit(
            "API token as <code>FOOTBALL_API<code> needed, get it from football-data.org...",
            del_in=5,
        )
        return
    input_ = message.filtered_input_str
    if input_:
        league_ = input_.split()[0]
        league_ = league_.upper()
    else:
        league_ = "PL"
    await message.edit("`Checking league code...`")

    try:
        connection = http.client.HTTPConnection("api.football-data.org")
        headers = {"X-Auth-Token": FOOTBALL_API}
        connection.request("GET", f"/v2/competitions/{league_}/matches", None, headers)
        response = json.loads(connection.getresponse().read().decode())
    except Exception as e:
        await message.err(e, del_in=5)
        return

    if "-j" in message.flags:
        json_ = json.dumps(response, indent=4)
        await message.edit_or_send_as_file(json_)
        return
    try:
        season_ = response["matches"][0]["season"]
    except BaseException:
        await message.edit(
            f"The given league code <code>{league_}</code> is wrong, please try again with correct league code...",
            del_in=5,
        )
        return
    start_ = (season_["startDate"]).split("-")[0]
    end_ = (season_["endDate"]).split("-")[0][2:]
    if start_[2:] == end_:
        start_end = start_
    else:
        start_end = f"{start_}/{end_}"
    league_ = response["competition"]["name"]
    country = response["competition"]["area"]["name"]
    try:
        cur_matchDay = input_.split()[1]
    except BaseException:
        cur_matchDay = season_["currentMatchday"]
    out_ = f"<b>LEAGUE:</b> <i>{league_} ({country}) {start_end}</i><br><br>"
    sr_ = 1
    for match_ in response["matches"]:
        stage_ = match_["stage"]
        if ("QUALIFICATION" or "PRELIMINARY") in stage_:
            continue
        stages = ["GROUP_STAGE", "ROUND_OF_16", "QUARTER_FINAL", "SEMI_FINAL", "FINAL"]
        if int(cur_matchDay) == match_["matchday"] and stage_ in stages:
            home_t = match_["homeTeam"]["name"]
            away_t = match_["awayTeam"]["name"]
            score = match_["score"]["fullTime"]
            h_score = score["homeTeam"]
            a_score = score["awayTeam"]
            if match_["status"] == "FINISHED":
                finished = True
                h_score = int(h_score)
                a_score = int(a_score)
                if h_score > a_score:
                    h_score = f"<b>{h_score}</b>"
                    home_t = f"<b>{home_t}</b>"
                elif h_score < a_score:
                    a_score = f"<b>{a_score}</b>"
                    away_t = f"<b>{away_t}</b>"
                else:
                    pass
            else:
                finished = False
                h_score = ""
                a_score = ""
            sche_ = match_["utcDate"]
            date_ = sche_.split("T")[0]
            date_ = date_.split("-")
            date_y = int(date_[0])
            date_m = int(date_[1])
            date_d = int(date_[2])
            time_ = sche_.split("T")[1]
            time_h = time_.split(":")[0]
            time_h = int(time_h)
            time_m = time_.split(":")[1]
            time_m = int(time_m)
            if FOOTBALL_UTC_TIME:
                differ = FOOTBALL_UTC_TIME
            else:
                differ = "+5:30"
            t_d_ = time_date_diff(
                year=date_y,
                month=date_m,
                date=date_d,
                hour=time_h,
                minute=time_m,
                diff=differ,
            )
            try:
                stage_now = f"<b>{match_['group']}</b><br>•"
            except BaseException:
                stage_now = "•"
            match_id = match_["id"]
            out_ += f"{stage_now} [{sr_}] <b>Match day:</b> <i>{cur_matchDay}</i> <b>Match ID:</b> <code>{match_id}</code><br>"
            if finished:
                out_ += f"{h_score} - {home_t}<br>" f"{a_score} - {away_t}<br>"
            else:
                out_ += f"{home_t}<br>" f"{away_t}<br>"
            out_ += f"{t_d_['date']}/{t_d_['month']}/{t_d_['year']} at {t_d_['hour']}:{t_d_['min']} {t_d_['stamp']} UTC{differ}<br><br>"
            sr_ += 1
    link_ = pt(f"Fixtures for {league_} this season ({start_end}).", out_)
    await message.edit(
        f"Fixtures for {league_} this season <i>({start_end})</i> is <a href='{link_}'><b>HERE</b></a>"
    )


@userge.on_cmd(
    "fbst",
    about={
        "header": "get competition standings",
        "flags": {"-j": "get entire json format"},
        "usage": "{tr}fbst [league code]",
    },
)
async def fb_stand_(message: Message):
    """get competition standings"""
    if not FOOTBALL_API:
        await message.edit(
            "API token as <code>FOOTBALL_API<code> needed, get it from football-data.org...",
            del_in=5,
        )
        return
    input_ = message.filtered_input_str
    if input_:
        league_ = input_.upper()
    else:
        league_ = "PL"
    await message.edit("`Checking league code...`")

    try:
        connection = http.client.HTTPConnection("api.football-data.org")
        headers = {"X-Auth-Token": FOOTBALL_API}
        connection.request(
            "GET", f"/v2/competitions/{league_}/standings", None, headers
        )
        response = json.loads(connection.getresponse().read().decode())
    except Exception as e:
        await message.err(e, del_in=5)
        return

    if "-j" in message.flags:
        json_ = json.dumps(response, indent=4)
        await message.edit_or_send_as_file(json_)
        return
    try:
        season_ = response["season"]
        stand_ = response["standings"]
    except BaseException:
        err = f"The given league code <code>{league_}</code> is wrong, please try again with correct league code...\n"
        if league_ == "WC" or league_ == "EC":
            err += "<b>NOTE:</b> <i>WC and EC are not available in this command.</i>"
        await message.edit(err, del_in=5)
        return
    start_ = (season_["startDate"]).split("-")[0]
    end_ = (season_["endDate"]).split("-")[0][2:]
    if start_[2:] == end_:
        start_end = start_
    else:
        start_end = f"{start_}/{end_}"
    md = season_["currentMatchday"]
    league_n = response["competition"]["name"]
    country = response["competition"]["area"]["name"]
    standings = f"<b>Standing table</b> for <b>{league_n}</b> ({country}) this season <i>({start_end})</i>: Match day {md}<br><br>"
    if league_ == "CL" or league_ == "CLI":
        stand_ = stand_[2:]
        for tables in stand_:
            tables["stage"]
            group_ = tables["group"]
            g_table = tables["table"]
            standings += f"<b>{group_}</b>:<br>"
            for one in g_table:
                position = one["position"]
                team_n = one["team"]["name"]
                played_ = one["playedGames"]
                won_ = one["won"]
                draw_ = one["draw"]
                lost_ = one["lost"]
                point_ = one["points"]
                standings += f"<b>{position:02}.</b> P-{played_:02} | W-{won_:02} | D-{draw_:02} | L-{lost_:02} | <b>{point_:02}</b> | {team_n}<br>"
            standings += "<br>"
    else:
        stand_ = stand_[0]["table"]
        for table in stand_:
            position = table["position"]
            team_n = table["team"]["name"]
            played_ = table["playedGames"]
            won_ = table["won"]
            draw_ = table["draw"]
            lost_ = table["lost"]
            point_ = table["points"]
            standings += f"<b>{position:02}.</b> P-{played_:02} | W-{won_:02} | D-{draw_:02} | L-{lost_:02} | <b>{point_:02}</b> | {team_n}<br>"
    link_ = pt(f"Standing table of {league_n} this season ({start_end}).", standings)
    await message.edit(
        f"Standing table of <b>{league_n}</b> this season <i>({start_end})</i> is <a href='{link_}'><b>HERE</b></a>"
    )
